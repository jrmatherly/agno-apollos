"""
M365 MCP Tools Layer
---------------------
Factory for Agno MCPTools connecting to the self-hosted Softeria ms-365-mcp-server.

Key design decisions:
- header_provider is SYNC (confirmed: agno/tools/mcp/mcp.py)
- contextvars propagates per-user Graph token from FastAPI request to header_provider
- Single MCPTools instance (one Softeria server) -- tool_name_prefix avoids collisions
- Server runs with --read-only -- write operations disabled at MCP server level
"""

from __future__ import annotations

import contextvars
import logging
from os import getenv
from typing import TYPE_CHECKING

from agno.tools.mcp import MCPTools

if TYPE_CHECKING:
    from agno.run import RunContext

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Per-request Graph token (set by middleware, read by header_provider)
# ---------------------------------------------------------------------------
_current_graph_token: contextvars.ContextVar[str] = contextvars.ContextVar("current_graph_token", default="")


def set_graph_token(token: str) -> None:
    """Set the current user's Graph token for this request context."""
    _current_graph_token.set(token)


def clear_graph_token() -> None:
    """Clear the Graph token after the request completes."""
    _current_graph_token.set("")


# ---------------------------------------------------------------------------
# header_provider -- SYNC, called by Agno without await
# ---------------------------------------------------------------------------
def m365_header_provider(run_context: RunContext, **_: object) -> dict[str, str]:
    """
    Injects the user's Graph access token as Authorization header.

    SYNC -- required by Agno (header_provider called without await).
    Reads from contextvars -- zero I/O, zero network.
    Returns {} if no token available (agent will prompt user to connect M365).
    """
    token = _current_graph_token.get()
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# MCP tools factory
# ---------------------------------------------------------------------------
_M365_MCP_URL = getenv("M365_MCP_URL", "http://apollos-m365-mcp:9000/mcp")


def m365_mcp_tools() -> list[MCPTools]:
    """
    Returns MCPTools for the self-hosted Softeria ms-365-mcp-server.

    Returns [] if M365_ENABLED is not true (safe to call unconditionally).
    """
    if getenv("M365_ENABLED", "").lower() not in ("true", "1", "yes"):
        return []

    return [
        MCPTools(
            url=_M365_MCP_URL,
            transport="streamable-http",
            header_provider=m365_header_provider,
            tool_name_prefix="m365",
        )
    ]


def m365_tools_factory() -> list[MCPTools]:
    """Callable tools factory for deferred MCP connection.

    Agno calls this per-run instead of at startup, avoiding the 401 that
    occurs when AgentOS ``mcp_lifespan`` connects before any user token exists.
    """
    return m365_mcp_tools()
