"""MCP Gateway configuration and shared state.

Provides ``get_gateway_client()`` and ``get_gateway_tools_factory()`` for
agents that route MCP traffic through the ContextForge gateway.

Reads ``MCP_GATEWAY_ENABLED``, ``MCP_GATEWAY_URL``, and
``MCP_GATEWAY_JWT_SECRET`` from the environment.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from os import getenv

from agno.tools.mcp import MCPTools

from backend.mcp.gateway_client import GatewayClient
from backend.mcp.tools_factory import create_gateway_header_provider

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Feature flag
# ---------------------------------------------------------------------------
MCP_GATEWAY_ENABLED = getenv("MCP_GATEWAY_ENABLED", "").lower() in ("true", "1", "yes")

# ---------------------------------------------------------------------------
# Shared client (lazy singleton)
# ---------------------------------------------------------------------------
_gateway_client: GatewayClient | None = None


def get_gateway_client() -> GatewayClient | None:
    """Return the shared gateway client, or None if the gateway is disabled."""
    global _gateway_client  # noqa: PLW0603
    if not MCP_GATEWAY_ENABLED:
        return None
    if _gateway_client is None:
        url = getenv("MCP_GATEWAY_URL", "http://apollos-mcp-gateway:4444")
        secret = getenv("MCP_GATEWAY_JWT_SECRET", "dev-gateway-secret")
        _gateway_client = GatewayClient(base_url=url, jwt_secret=secret)
        log.info("MCP Gateway client initialized: %s", url)
    return _gateway_client


# ---------------------------------------------------------------------------
# Server ID cache — populated lazily from gateway registry (5 min TTL)
# ---------------------------------------------------------------------------
_SERVER_ID_TTL = 300  # seconds
_server_ids: dict[str, tuple[str, float]] = {}


async def _resolve_server_id(name: str) -> str | None:
    """Resolve a server name to its gateway ID, caching the result."""
    cached = _server_ids.get(name)
    if cached and (time.monotonic() - cached[1]) < _SERVER_ID_TTL:
        return cached[0]
    client = get_gateway_client()
    if not client:
        return None
    server_id = await client.get_server_id_by_name(name)
    if server_id:
        _server_ids[name] = (server_id, time.monotonic())
    return server_id


def get_gateway_tools_factory(
    server_name: str,
    *,
    needs_user_token: bool = False,
) -> Callable[[], list[MCPTools]] | None:
    """Return a callable tools factory that routes through the gateway.

    Returns ``None`` if the gateway is disabled, allowing callers to fall back
    to their default tools factory::

        tools = get_gateway_tools_factory("m365", needs_user_token=True) or m365_tools_factory

    The factory uses ``header_provider`` (not ``server_params``) to match the
    established M365 convention. Server ID resolution is deferred — the factory
    builds the MCP URL from ``MCP_GATEWAY_URL`` and the server name directly,
    which works when server names are registered as URL-safe slugs.
    """
    client = get_gateway_client()
    if not client:
        return None

    provider = create_gateway_header_provider(client, needs_user_token=needs_user_token)

    # Build URL directly from server name — avoids async server ID lookup at
    # module import time. ContextForge supports /servers/{name}/mcp when the
    # server is registered with a slug-safe name.
    gateway_url = getenv("MCP_GATEWAY_URL", "http://apollos-mcp-gateway:4444").rstrip("/")

    def factory() -> list[MCPTools]:
        return [
            MCPTools(
                url=f"{gateway_url}/servers/{server_name}/mcp",
                transport="streamable-http",
                header_provider=provider,
                tool_name_prefix=server_name,
                refresh_connection=True,
            )
        ]

    return factory
