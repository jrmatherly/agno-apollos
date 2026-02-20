from fastapi import APIRouter, Depends, Request
from sqlalchemy import select

from backend.auth.config import auth_config
from backend.auth.database import get_auth_session
from backend.auth.dependencies import get_current_user, require_scope
from backend.auth.models import AuthTeam, AuthUser
from backend.auth.scope_mapper import roles_to_scopes
from backend.auth.sync_service import sync_service  # Module-level singleton

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.get("/health")
async def auth_health():  # type: ignore[return]
    """Auth subsystem health check — no auth required."""
    return {"status": "ok", "auth_enabled": auth_config.enabled}


@auth_router.get("/me")
async def get_me(payload: dict = Depends(get_current_user)):  # type: ignore[type-arg, return]
    """Current user profile, roles, and computed scopes."""
    roles: list[str] = payload.get("roles", [])
    return {
        "oid": payload.get("oid"),
        "email": payload.get("preferred_username"),
        "name": payload.get("name"),
        "roles": roles,
        "scopes": roles_to_scopes(roles),
    }


@auth_router.post("/sync")
async def sync_user(request: Request, payload: dict = Depends(get_current_user)):  # type: ignore[type-arg, return]
    """Trigger on-demand group sync using user's token."""
    await sync_service.sync_user_on_login(request.state.token, payload)
    return {"status": "synced"}


@auth_router.get("/teams")
async def list_teams(  # type: ignore[return]
    _=require_scope("teams:read"),
    session=Depends(get_auth_session),
):
    """List all active teams."""
    result = await session.execute(
        select(AuthTeam).where(AuthTeam.is_active == True)  # noqa: E712
    )
    teams = result.scalars().all()
    return [
        {"id": str(t.id), "name": t.name, "source": t.source, "description": t.description}
        for t in teams
    ]


@auth_router.get("/users")
async def list_users(  # type: ignore[return]
    _=require_scope("agent_os:admin"),
    session=Depends(get_auth_session),
):
    """List all active users (admin only)."""
    result = await session.execute(
        select(AuthUser).where(AuthUser.is_active == True)  # noqa: E712
    )
    users = result.scalars().all()
    return [
        {"oid": u.oid, "email": u.email, "name": u.display_name, "roles": u.roles}
        for u in users
    ]
