"""
OBO Token Service for Microsoft 365 MCP Integration
----------------------------------------------------
Per-user MSAL ConfidentialClientApplication instances with SerializableTokenCache.

Token flow:
1. connect(): OBO exchange (Apollos JWT -> Graph token). ~200-500ms network call.
2. get_graph_token(): acquire_token_silent (cache hit ~0ms, refresh ~200ms once/hour).
3. disconnect(): Clear user's MSAL app + DB cache state.

MSAL cache persisted to PostgreSQL (encrypted via Fernet) for restart survival.
Per-user instances ensure token isolation -- no cross-user leakage.
"""

from __future__ import annotations

import base64
import hashlib
import logging
import threading
from os import getenv
from typing import Any

import msal
from cryptography.fernet import Fernet

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Graph scopes -- admin pre-consented, read-only
# ---------------------------------------------------------------------------
GRAPH_SCOPES: list[str] = [
    "https://graph.microsoft.com/.default",
    "offline_access",
]

# ---------------------------------------------------------------------------
# Encryption for token cache persistence
# ---------------------------------------------------------------------------
_CACHE_KEY: str | None = None


def _get_fernet() -> Fernet:
    """Get Fernet instance for encrypting/decrypting MSAL cache state."""
    global _CACHE_KEY
    if _CACHE_KEY is None:
        key = getenv("M365_CACHE_KEY", "")
        if not key:
            # Derive from client secret (acceptable for dev, not production)
            secret = getenv("AZURE_CLIENT_SECRET", "default-dev-key-not-for-prod")
            derived = hashlib.sha256(secret.encode()).digest()
            key = base64.urlsafe_b64encode(derived).decode()
        _CACHE_KEY = key
    return Fernet(_CACHE_KEY.encode() if isinstance(_CACHE_KEY, str) else _CACHE_KEY)


def encrypt_cache(plaintext: str) -> bytes:
    """Encrypt MSAL cache state for DB storage."""
    return _get_fernet().encrypt(plaintext.encode())


def decrypt_cache(ciphertext: bytes) -> str:
    """Decrypt MSAL cache state from DB storage."""
    return _get_fernet().decrypt(ciphertext).decode()


# ---------------------------------------------------------------------------
# OBOTokenService
# ---------------------------------------------------------------------------
class OBOTokenService:
    """
    Manages per-user MSAL apps for OBO token exchange with Microsoft Graph.

    Each user gets their own ConfidentialClientApplication with an isolated
    SerializableTokenCache. This prevents cross-user token leakage and allows
    independent cache persistence.
    """

    def __init__(self, tenant_id: str, client_id: str, client_secret: str) -> None:
        self._tenant_id = tenant_id
        self._client_id = client_id
        self._client_secret = client_secret
        self._authority = f"https://login.microsoftonline.com/{tenant_id}"

        # Per-user MSAL app instances (isolated token caches)
        self._user_apps: dict[str, msal.ConfidentialClientApplication] = {}
        # Per-user locks (prevent concurrent OBO calls per user)
        self._user_locks: dict[str, threading.Lock] = {}

    def _get_lock(self, user_oid: str) -> threading.Lock:
        """Get or create per-user lock. Uses setdefault for atomic creation."""
        return self._user_locks.setdefault(user_oid, threading.Lock())

    def _get_or_create_app(self, user_oid: str, cache_state: str | None = None) -> msal.ConfidentialClientApplication:
        """Get or create per-user MSAL app with isolated token cache."""
        if user_oid in self._user_apps:
            return self._user_apps[user_oid]
        cache = msal.SerializableTokenCache()
        if cache_state:
            cache.deserialize(cache_state)
        app = msal.ConfidentialClientApplication(
            client_id=self._client_id,
            client_credential=self._client_secret,
            authority=self._authority,
            token_cache=cache,
        )
        self._user_apps.setdefault(user_oid, app)
        return self._user_apps[user_oid]

    def connect(self, user_oid: str, user_jwt: str) -> dict[str, Any]:
        """
        OBO exchange: user's Apollos JWT -> Graph access token.

        SYNC -- call via asyncio.to_thread() from async route handlers.

        Returns:
            {"connected": True, "scopes": [...]} on success
            {"connected": False, "error": "..."} on failure
        """
        app = self._get_or_create_app(user_oid)
        scopes = [s for s in GRAPH_SCOPES if s != "offline_access"]

        with self._get_lock(user_oid):
            result = app.acquire_token_on_behalf_of(
                user_assertion=user_jwt,
                scopes=scopes + ["offline_access"],
            )

        if "access_token" not in result:
            error = result.get("error_description", result.get("error", "OBO exchange failed"))
            log.warning("OBO exchange failed for user %s: %s", user_oid, error)
            return {"connected": False, "error": error}

        granted_scopes = result.get("scope", "").split()
        log.info("M365 OBO exchange succeeded for user %s -- %d scopes", user_oid, len(granted_scopes))
        return {"connected": True, "scopes": granted_scopes}

    def get_graph_token(self, user_oid: str) -> str | None:
        """
        Returns current Graph access token for the user.

        SYNC -- compatible with Agno's synchronous header_provider callback.
        Cache hit: zero I/O (~0ms). Cache miss/refresh: ~200ms (once/hour/user).

        Returns None if user hasn't connected or refresh token expired.
        """
        app = self._user_apps.get(user_oid)
        if not app:
            return None

        accounts = app.get_accounts()
        if not accounts:
            return None

        scopes = [s for s in GRAPH_SCOPES if s != "offline_access"]

        with self._get_lock(user_oid):
            result = app.acquire_token_silent(scopes=scopes, account=accounts[0])

        if result and "access_token" in result:
            return result["access_token"]

        # Silent acquisition failed -- refresh token may be expired
        error = (result or {}).get("error_description", "silent acquisition failed")
        log.info("Token refresh failed for user %s: %s", user_oid, error)
        return None

    def disconnect(self, user_oid: str) -> None:
        """Remove user's MSAL app and cached tokens."""
        self._user_apps.pop(user_oid, None)
        self._user_locks.pop(user_oid, None)
        log.info("User %s disconnected from M365", user_oid)

    def status(self, user_oid: str) -> dict[str, Any]:
        """Connection status for Settings UI."""
        app = self._user_apps.get(user_oid)
        if not app:
            return {"connected": False}
        accounts = app.get_accounts()
        if not accounts:
            return {"connected": False, "needs_reconnect": True}
        return {"connected": True, "account": accounts[0].get("username", "")}

    def get_cache_state(self, user_oid: str) -> str | None:
        """Serialize user's MSAL cache for encrypted DB persistence."""
        app = self._user_apps.get(user_oid)
        if not app or not app.token_cache.has_state_changed:
            return None
        return app.token_cache.serialize()

    def restore_cache(self, user_oid: str, cache_state: str) -> None:
        """Restore user's MSAL cache from DB on startup."""
        self._get_or_create_app(user_oid, cache_state=cache_state)
        log.debug("Restored M365 cache for user %s", user_oid)


# ---------------------------------------------------------------------------
# Module-level singleton -- lazily initialized
# ---------------------------------------------------------------------------
_obo_service: OBOTokenService | None = None


def get_obo_service() -> OBOTokenService:
    """Get or create the OBOTokenService singleton."""
    global _obo_service
    if _obo_service is None:
        from backend.auth.config import auth_config

        _obo_service = OBOTokenService(
            tenant_id=auth_config.tenant_id,
            client_id=auth_config.client_id,
            client_secret=auth_config.client_secret,
        )
    return _obo_service
