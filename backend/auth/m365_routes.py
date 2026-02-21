"""
M365 Settings API Routes
------------------------
Mounted at /m365/ on base_app when M365_ENABLED=true.

GET  /m365/status     -- connection status for Settings UI
POST /m365/connect    -- OBO exchange (rate limited: 5/minute)
POST /m365/disconnect -- clear connection
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Request
from sqlalchemy import select

from backend.auth.m365_token_service import decrypt_cache, encrypt_cache, get_obo_service
from backend.auth.routes import limiter

log = logging.getLogger(__name__)

m365_router = APIRouter(prefix="/m365", tags=["m365"])


@m365_router.get("/status")
@limiter.limit("30/minute")
async def m365_status(request: Request) -> dict:  # type: ignore[return]
    """Returns M365 connection status for the authenticated user."""
    if not getattr(request.state, "authenticated", False):
        raise HTTPException(status_code=401, detail="Not authenticated")

    user_oid = getattr(request.state, "user_id", None)
    if not user_oid:
        raise HTTPException(status_code=401, detail="User ID not available")

    service = get_obo_service()
    return service.status(user_oid)


@m365_router.post("/connect")
@limiter.limit("5/minute")
async def m365_connect(request: Request) -> dict:  # type: ignore[return]
    """OBO exchange: user's Apollos JWT -> Graph access token."""
    if not getattr(request.state, "authenticated", False):
        raise HTTPException(status_code=401, detail="Not authenticated")

    user_oid = getattr(request.state, "user_id", None)
    token = getattr(request.state, "token", None)
    if not user_oid or not token:
        raise HTTPException(status_code=400, detail="Auth context incomplete")

    service = get_obo_service()

    # OBO exchange -- synchronous MSAL call, run in thread to avoid blocking event loop
    result = await asyncio.to_thread(service.connect, user_oid, token)

    if not result.get("connected"):
        log.warning("M365 connect failed for user %s", user_oid)
        raise HTTPException(status_code=400, detail="Failed to connect Microsoft 365. Please try again.")

    # Persist connection + encrypted cache to DB
    try:
        cache_state = service.get_cache_state(user_oid)
        await _persist_connection(user_oid, result.get("scopes", []), cache_state)
    except Exception as exc:
        log.error("Failed to persist M365 connection for user %s: %s", user_oid, exc)

    return {"connected": True, "scopes": result.get("scopes", [])}


@m365_router.post("/disconnect")
@limiter.limit("10/minute")
async def m365_disconnect(request: Request) -> dict:  # type: ignore[return]
    """Clears M365 connection."""
    if not getattr(request.state, "authenticated", False):
        raise HTTPException(status_code=401, detail="Not authenticated")

    user_oid = getattr(request.state, "user_id", None)
    if not user_oid:
        raise HTTPException(status_code=401, detail="User ID not available")

    service = get_obo_service()
    service.disconnect(user_oid)

    try:
        await _clear_connection(user_oid)
    except Exception as exc:
        log.error("Failed to clear M365 connection for user %s: %s", user_oid, exc)

    return {"disconnected": True}


# ---------------------------------------------------------------------------
# DB helpers (async -- only called from route handlers)
# ---------------------------------------------------------------------------
async def _persist_connection(user_oid: str, scopes: list[str], cache_state: str | None) -> None:
    """Upsert M365Connection row with encrypted cache."""
    from backend.auth.database import auth_session_factory
    from backend.auth.models import AuthUser, M365Connection

    async with auth_session_factory() as session:
        user_row = await session.execute(select(AuthUser).where(AuthUser.oid == user_oid))
        user = user_row.scalar_one_or_none()
        if not user:
            return

        result = await session.execute(select(M365Connection).where(M365Connection.user_id == user.id))
        conn = result.scalar_one_or_none()

        now = datetime.now(timezone.utc)
        encrypted = encrypt_cache(cache_state) if cache_state else None

        if conn:
            conn.connected_at = now
            conn.last_refreshed = now
            conn.scopes = " ".join(scopes)
            conn.cache_state = encrypted
            conn.is_active = True
        else:
            conn = M365Connection(
                user_id=user.id,
                connected_at=now,
                last_refreshed=now,
                scopes=" ".join(scopes),
                cache_state=encrypted,
                is_active=True,
            )
            session.add(conn)

        await session.commit()


async def _clear_connection(user_oid: str) -> None:
    """Mark M365Connection as inactive, clear cache."""
    from backend.auth.database import auth_session_factory
    from backend.auth.models import AuthUser, M365Connection

    async with auth_session_factory() as session:
        user_row = await session.execute(select(AuthUser).where(AuthUser.oid == user_oid))
        user = user_row.scalar_one_or_none()
        if not user:
            return

        result = await session.execute(select(M365Connection).where(M365Connection.user_id == user.id))
        conn = result.scalar_one_or_none()
        if conn:
            conn.is_active = False
            conn.cache_state = None
            await session.commit()


async def warm_m365_cache() -> None:
    """Load active M365 connections from DB into MSAL caches at startup."""
    from backend.auth.database import auth_session_factory
    from backend.auth.models import AuthUser, M365Connection

    service = get_obo_service()
    async with auth_session_factory() as session:
        result = await session.execute(
            select(M365Connection, AuthUser.oid)
            .join(AuthUser, M365Connection.user_id == AuthUser.id)
            .where(M365Connection.is_active == True)  # noqa: E712
        )
        rows = result.all()
        restored = 0
        for conn, user_oid in rows:
            if conn.cache_state:
                try:
                    cache_state = decrypt_cache(conn.cache_state)
                    service.restore_cache(user_oid, cache_state)
                    restored += 1
                except Exception as exc:
                    log.warning("Failed to restore M365 cache for user %s: %s", user_oid, exc)
        log.info("Warmed M365 cache: %d/%d connections restored", restored, len(rows))
