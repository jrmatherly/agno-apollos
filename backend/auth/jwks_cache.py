import asyncio
import time
from typing import Any, Callable

import httpx
from jwt.algorithms import RSAAlgorithm

from backend.auth.config import auth_config


class JWKSCache:
    def __init__(self, oidc_discovery_url: str, refresh_interval: int = 3600, miss_cooldown: int = 300):
        self._discovery_url = oidc_discovery_url
        self._refresh_interval = refresh_interval
        self._miss_cooldown = miss_cooldown
        self._keys: dict[str, Any] = {}  # kid → RSA public key object
        self._jwks_uri: str = ""
        self._last_miss_fetch: float = 0.0
        self._callbacks: list[Callable[[], None]] = []
        self._client = httpx.AsyncClient(timeout=10.0)

    async def initialize(self) -> None:
        """Fetch OIDC discovery doc and load initial JWKS. Call in lifespan startup."""
        self._jwks_uri = await self._discover_jwks_uri()
        await self._fetch_keys()

    def on_refresh(self, callback: Callable[[], None]) -> None:
        """Register a callback to invoke after each key refresh."""
        self._callbacks.append(callback)

    def get_key(self, kid: str) -> Any | None:
        """Get a public key by kid. Returns None if not found."""
        return self._keys.get(kid)

    async def fetch_on_miss(self, kid: str) -> Any | None:
        """
        Re-fetch JWKS when a kid is not found in cache.
        Throttled: no re-fetch if last attempt < miss_cooldown seconds ago.
        Returns the key if found after refresh, None otherwise.
        """
        now = time.monotonic()
        if now - self._last_miss_fetch < self._miss_cooldown:
            return None  # Too soon — prevent stampede
        self._last_miss_fetch = now
        await self._fetch_keys()
        return self._keys.get(kid)

    async def run(self) -> None:
        """Background refresh loop. Run as asyncio task in lifespan."""
        while True:
            await asyncio.sleep(self._refresh_interval)
            try:
                await self._fetch_keys()
            except Exception:
                pass  # Log error but don't crash the background task

    async def _discover_jwks_uri(self) -> str:
        """Fetch OIDC discovery document and extract jwks_uri."""
        resp = await self._client.get(self._discovery_url)
        resp.raise_for_status()
        return str(resp.json()["jwks_uri"])

    async def _fetch_keys(self) -> None:
        """Download JWKS and update in-memory key cache."""
        resp = await self._client.get(self._jwks_uri)
        resp.raise_for_status()
        keys: dict[str, Any] = {}
        for jwk in resp.json().get("keys", []):
            kid = jwk.get("kid")
            if kid and jwk.get("kty") == "RSA":
                public_key = RSAAlgorithm.from_jwk(jwk)
                keys[kid] = public_key
        self._keys = keys
        for cb in self._callbacks:
            try:
                cb()
            except Exception:
                pass

    async def close(self) -> None:
        await self._client.aclose()


# Module-level singleton — created at import time, initialized in auth_lifespan
jwks_cache = JWKSCache(
    oidc_discovery_url=auth_config.oidc_discovery_url,
    refresh_interval=auth_config.jwks_refresh_interval,
    miss_cooldown=auth_config.jwks_miss_cooldown,
)
