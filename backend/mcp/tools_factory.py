"""Gateway-aware MCPTools factories.

Creates callable tools factories that route MCP traffic through the ContextForge
gateway. Uses the ``header_provider`` pattern (matching the M365 convention in
``backend/tools/m365.py``) — NOT ``server_params``.

Key design decisions:
- Zero-param factory: Agno calls ``factory()`` per-run when ``tools=factory``
- ``header_provider`` is SYNC: Agno calls without ``await``
- Service JWT includes ``jti`` + ``exp`` per RC1 requirements
- ``refresh_connection=True``: forces per-run MCP connection with fresh headers
- ``cache_callables=False`` must be set on the **Agent** (not here) for per-user isolation
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import TYPE_CHECKING

from agno.tools.mcp import MCPTools

from backend.mcp.gateway_client import GatewayClient

if TYPE_CHECKING:
    from agno.run import RunContext

log = logging.getLogger(__name__)


def create_gateway_header_provider(
    gateway_client: GatewayClient,
    *,
    needs_user_token: bool = False,
) -> Callable[..., dict[str, str]]:
    """Create a header_provider callback for MCPTools.

    1. Generates a fresh gateway service JWT (with jti + exp per RC1)
    2. Optionally forwards the user's Graph token via X-Upstream-Authorization

    Returns a SYNC callable — Agno's header_provider must be sync.
    """

    def header_provider(run_context: RunContext | None = None, **_: object) -> dict[str, str]:
        headers: dict[str, str] = {
            "Authorization": f"Bearer {gateway_client.create_service_token()}",
        }

        if needs_user_token and run_context:
            user_id = getattr(run_context, "user_id", None)
            if user_id:
                from backend.auth.m365_token_service import get_obo_service

                graph_token = get_obo_service().get_graph_token(user_id)
                if graph_token:
                    headers["X-Upstream-Authorization"] = f"Bearer {graph_token}"

        return headers

    return header_provider


def create_gateway_tools_factory(
    gateway_client: GatewayClient,
    server_id: str,
    server_name: str,
    *,
    needs_user_token: bool = False,
) -> Callable[[], list[MCPTools]]:
    """Create a callable tools factory for an Agno agent.

    Uses zero-param factory + header_provider pattern (matching M365 convention).
    """
    mcp_url = gateway_client.get_server_mcp_url(server_id)
    provider = create_gateway_header_provider(gateway_client, needs_user_token=needs_user_token)

    def factory() -> list[MCPTools]:
        return [
            MCPTools(
                url=mcp_url,
                transport="streamable-http",
                header_provider=provider,
                tool_name_prefix=server_name,
                refresh_connection=True,
            )
        ]

    return factory
