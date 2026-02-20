import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from backend.auth.config import auth_config
from backend.auth.jwks_cache import jwks_cache
from backend.auth.middleware import EntraJWTMiddleware
from backend.auth.routes import auth_router
from backend.auth.sync_service import sync_service


@asynccontextmanager
async def auth_lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Agno-compatible lifespan for auth subsystem initialization.

    On startup:  initializes JWKS cache, creates auth DB tables, starts background tasks.
    On shutdown: cancels background tasks, closes HTTP clients.

    Pass to AgentOS(lifespan=auth_lifespan) — Agno wraps existing lifespans.
    When auth_config.enabled is False, startup/shutdown are no-ops (local dev passthrough).
    """
    from backend.auth.database import create_auth_tables

    jwks_task: asyncio.Task | None = None
    sync_task: asyncio.Task | None = None

    if auth_config.enabled:
        await jwks_cache.initialize()
        await create_auth_tables()
        jwks_task = asyncio.create_task(jwks_cache.run())
        sync_task = asyncio.create_task(sync_service.run_background_sync())

    yield

    # Shutdown — cancel background tasks, close HTTP clients
    if jwks_task:
        jwks_task.cancel()
    if sync_task:
        sync_task.cancel()
    if auth_config.enabled:
        await jwks_cache.close()


__all__ = [
    "EntraJWTMiddleware",
    "auth_router",
    "auth_lifespan",
    "auth_config",
    "jwks_cache",
    "sync_service",
]
