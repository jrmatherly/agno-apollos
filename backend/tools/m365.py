"""
M365 MCP Tools Layer
---------------------
Factory for Agno MCPTools connecting to the self-hosted Softeria ms-365-mcp-server.

Key design decisions:
- header_provider is SYNC (confirmed: agno/tools/mcp/mcp.py calls without await)
- header_provider reads Graph token directly from OBOTokenService using run_context.user_id
  — no middleware, no contextvars, no cancel scope issues
- Single MCPTools instance (one Softeria server) -- tool_name_prefix avoids collisions
- Server runs with --read-only -- write operations disabled at MCP server level
"""

from __future__ import annotations

import logging
from os import getenv
from typing import TYPE_CHECKING

from agno.tools.mcp import MCPTools

if TYPE_CHECKING:
    from agno.run import RunContext

log = logging.getLogger(__name__)

_M365_MCP_URL = getenv("M365_MCP_URL", "http://apollos-m365-mcp:9000/mcp")


# ---------------------------------------------------------------------------
# header_provider -- SYNC, called by Agno per-request with run_context
# ---------------------------------------------------------------------------
def m365_header_provider(run_context: RunContext, **_: object) -> dict[str, str]:
    """
    Injects the user's Graph access token as Authorization header.

    SYNC -- required by Agno (header_provider called without await).
    Gets token directly from OBOTokenService via run_context.user_id.
    Returns {} if no token available (agent will prompt user to connect M365).
    """
    user_id = getattr(run_context, "user_id", None) if run_context else None
    if not user_id:
        return {}

    from backend.auth.m365_token_service import get_obo_service

    token = get_obo_service().get_graph_token(user_id)
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# MCP tools factory
# ---------------------------------------------------------------------------
def m365_tools_factory() -> list[MCPTools]:
    """Callable tools factory for deferred MCP connection.

    Agno calls this per-run instead of at startup, avoiding the 401 that
    occurs when AgentOS ``mcp_lifespan`` connects before any user token exists.

    Always returns the MCPTools list -- the header_provider handles per-user
    token resolution at call time, returning {} when no token is available.
    """
    if getenv("M365_ENABLED", "").lower() not in ("true", "1", "yes"):
        return []

    return [
        MCPTools(
            url=_M365_MCP_URL,
            transport="streamable-http",
            header_provider=m365_header_provider,
            tool_name_prefix="m365",
            refresh_connection=True,
        )
    ]
