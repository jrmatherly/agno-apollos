import asyncio
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from backend.auth.config import auth_config
from backend.auth.database import auth_session_factory
from backend.auth.graph import GraphClient
from backend.auth.models import AuthDeniedToken, AuthTeam, AuthTeamMembership, AuthUser


class SyncService:
    def __init__(self, graph_client: GraphClient, sync_interval: int = 900):
        self._graph = graph_client
        self._sync_interval = sync_interval

    async def sync_user_on_login(self, user_token: str, payload: dict) -> None:  # type: ignore[type-arg]
        """
        Called at login time with the user's delegated token.
        Upserts user record and syncs group memberships.
        """
        oid = payload["oid"]
        tid = payload.get("tid", "")
        email = payload.get("preferred_username", payload.get("email", ""))
        display_name = payload.get("name", "")
        roles: list[str] = payload.get("roles", [])

        # Check groups-overage indicator (>200 groups)
        has_overage = "_claim_names" in payload and "groups" in payload.get("_claim_names", {})
        if has_overage or "groups" not in payload:
            groups = await self._graph.get_user_groups_delegated(user_token)
        else:
            groups = [{"id": g} for g in payload.get("groups", [])]

        async with auth_session_factory() as session:
            # Upsert user
            stmt = (
                insert(AuthUser)
                .values(
                    oid=oid,
                    tid=tid,
                    email=email,
                    display_name=display_name,
                    roles=roles,
                    last_synced=datetime.now(timezone.utc),
                )
                .on_conflict_do_update(
                    index_elements=["oid"],
                    set_={
                        "email": email,
                        "display_name": display_name,
                        "roles": roles,
                        "last_synced": datetime.now(timezone.utc),
                    },
                )
            )
            await session.execute(stmt)

            # Get internal user ID
            result = await session.execute(select(AuthUser).where(AuthUser.oid == oid))
            user = result.scalar_one()

            # Sync team memberships from groups
            group_ids = {g["id"] for g in groups}
            teams_result = await session.execute(
                select(AuthTeam).where(
                    AuthTeam.group_id.in_(group_ids),
                    AuthTeam.is_active == True,  # noqa: E712
                )
            )
            for team in teams_result.scalars():
                mem_stmt = (
                    insert(AuthTeamMembership)
                    .values(
                        team_id=team.id,
                        user_id=user.id,
                        role="member",
                        joined_at=datetime.now(timezone.utc),
                    )
                    .on_conflict_do_nothing()
                )
                await session.execute(mem_stmt)

            await session.commit()

    async def run_background_sync(self) -> None:
        """Background task: periodically re-sync active users."""
        while True:
            await asyncio.sleep(self._sync_interval)
            try:
                await self._sync_active_users()
            except Exception:
                pass  # Log and continue

    async def _sync_active_users(self) -> None:
        """Re-sync users who have been active in the last 8 hours."""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=8)
        async with auth_session_factory() as session:
            result = await session.execute(
                select(AuthUser).where(
                    AuthUser.is_active == True,  # noqa: E712
                    AuthUser.last_synced >= cutoff,
                )
            )
            users = result.scalars().all()

        for user in users:
            try:
                info = await self._graph.get_user_info(user.oid)
                if info and not info.get("accountEnabled", True):
                    await self._deny_user(user.oid, "deprovisioned")
            except Exception:
                pass

    async def _deny_user(self, oid: str, reason: str) -> None:
        """Add user to deny list (2h from now for safety margin)."""
        async with auth_session_factory() as session:
            denial = AuthDeniedToken(
                id=uuid.uuid4(),
                oid=oid,
                reason=reason,
                expires_at=datetime.now(timezone.utc) + timedelta(hours=2),
            )
            session.add(denial)
            await session.commit()


# Module-level singletons — created at import time, initialized in auth_lifespan
_graph_client = GraphClient(
    tenant_id=auth_config.tenant_id,
    client_id=auth_config.client_id,
    client_secret=auth_config.client_secret,
)

sync_service = SyncService(
    graph_client=_graph_client,
    sync_interval=auth_config.group_sync_interval,
)
