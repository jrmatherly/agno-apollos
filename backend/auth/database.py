from collections.abc import AsyncGenerator
from os import getenv

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.auth.models import AuthBase

# Build DB URL from project env vars (matches docker-compose.yaml / mise.toml defaults)
_db_url = (
    "postgresql+psycopg://"
    f"{getenv('DB_USER', 'ai')}:{getenv('DB_PASS', 'ai')}"
    f"@{getenv('DB_HOST', 'apollos-db')}:{getenv('DB_PORT', '5432')}"
    f"/{getenv('DB_DATABASE', 'ai')}"
)

_engine = create_async_engine(_db_url, pool_pre_ping=True)
auth_session_factory = async_sessionmaker(_engine, expire_on_commit=False)


async def create_auth_tables() -> None:
    """Create auth tables if they don't exist. Called in lifespan startup."""
    async with _engine.begin() as conn:
        await conn.run_sync(AuthBase.metadata.create_all)


async def get_auth_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency: yields an async DB session."""
    async with auth_session_factory() as session:
        yield session
