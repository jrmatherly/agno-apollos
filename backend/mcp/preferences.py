"""Per-user MCP workspace preferences (PostgreSQL-backed)."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.models import MCPPreference
from backend.mcp.schemas import MCPUserPreferences

log = logging.getLogger(__name__)

_DEFAULT_PREFS = MCPUserPreferences()


async def get_preferences(session: AsyncSession, user_id: str) -> MCPUserPreferences:
    """Load preferences for a user, returning defaults if none exist."""
    from backend.auth.models import AuthUser

    # Resolve Entra OID string to internal UUID
    user_result = await session.execute(select(AuthUser.id).where(AuthUser.oid == user_id))
    auth_user_id = user_result.scalar_one_or_none()
    if not auth_user_id:
        return _DEFAULT_PREFS

    pref_result = await session.execute(select(MCPPreference).where(MCPPreference.user_id == auth_user_id))
    row = pref_result.scalar_one_or_none()
    if not row:
        return _DEFAULT_PREFS

    return MCPUserPreferences(
        hidden_tools=row.hidden_tools,
        hidden_servers=row.hidden_servers,
        default_tab=row.default_tab,
        compact_view=row.compact_view,
    )


async def save_preferences(session: AsyncSession, user_id: str, prefs: MCPUserPreferences) -> None:
    """Save preferences for a user (upsert)."""
    from backend.auth.models import AuthUser

    user_result = await session.execute(select(AuthUser.id).where(AuthUser.oid == user_id))
    auth_user_id = user_result.scalar_one_or_none()
    if not auth_user_id:
        raise ValueError(f"User {user_id} not found in auth_users")

    pref_result = await session.execute(select(MCPPreference).where(MCPPreference.user_id == auth_user_id))
    row = pref_result.scalar_one_or_none()

    if row:
        row.hidden_tools = prefs.hidden_tools
        row.hidden_servers = prefs.hidden_servers
        row.default_tab = prefs.default_tab
        row.compact_view = prefs.compact_view
        row.updated_at = datetime.now(timezone.utc)
    else:
        row = MCPPreference(
            user_id=auth_user_id,
            hidden_tools=prefs.hidden_tools,
            hidden_servers=prefs.hidden_servers,
            default_tab=prefs.default_tab,
            compact_view=prefs.compact_view,
        )
        session.add(row)

    await session.commit()
