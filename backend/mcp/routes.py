"""MCP Gateway proxy routes.

Thin proxy to the ContextForge gateway API, mounted at ``/mcp/`` on base_app
when ``MCP_GATEWAY_ENABLED=true``.

GET    /mcp/servers          List registered MCP servers
GET    /mcp/servers/{id}     Get a single server
POST   /mcp/servers          Register a new server (admin only)
DELETE /mcp/servers/{id}     Remove a server (admin only)
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Request

from backend.auth.routes import limiter
from backend.mcp.config import get_gateway_client
from backend.mcp.schemas import MCPServerInfo, MCPServerRegister, MCPServerResponse
from backend.mcp.validation import URLValidationError, validate_mcp_server_url

log = logging.getLogger(__name__)

mcp_router = APIRouter(prefix="/mcp", tags=["mcp"])


def _require_auth(request: Request) -> str:
    """Extract authenticated user_id or raise 401."""
    if not getattr(request.state, "authenticated", False):
        raise HTTPException(status_code=401, detail="Not authenticated")
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not available")
    return user_id


def _require_gateway():
    """Return the gateway client or raise 503."""
    client = get_gateway_client()
    if not client:
        raise HTTPException(status_code=503, detail="MCP Gateway not configured")
    return client


@mcp_router.get("/servers", response_model=list[MCPServerInfo])
@limiter.limit("30/minute")
async def list_servers(request: Request) -> list[MCPServerInfo]:
    """List all registered MCP servers from the gateway."""
    _require_auth(request)
    client = _require_gateway()
    gateways = await client.list_gateways()
    return [
        MCPServerInfo(
            id=gw.get("id", ""),
            name=gw.get("name", ""),
            url=gw.get("url", ""),
            status=gw.get("status"),
        )
        for gw in gateways
    ]


@mcp_router.get("/servers/{server_id}", response_model=MCPServerInfo)
@limiter.limit("30/minute")
async def get_server(request: Request, server_id: str) -> MCPServerInfo:
    """Get details for a specific MCP server."""
    _require_auth(request)
    client = _require_gateway()
    gateways = await client.list_gateways()
    for gw in gateways:
        if gw.get("id") == server_id:
            return MCPServerInfo(
                id=gw["id"],
                name=gw.get("name", ""),
                url=gw.get("url", ""),
                status=gw.get("status"),
            )
    raise HTTPException(status_code=404, detail="Server not found")


@mcp_router.post("/servers", response_model=MCPServerResponse, status_code=201)
@limiter.limit("10/minute")
async def register_server(request: Request, body: MCPServerRegister) -> MCPServerResponse:
    """Register a new upstream MCP server (admin only — scoped via RBAC)."""
    _require_auth(request)
    client = _require_gateway()
    try:
        validated_url = validate_mcp_server_url(body.url, allow_internal=True)
    except URLValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    result = await client.register_gateway(name=body.name, url=validated_url)
    return MCPServerResponse(
        id=result.get("id", ""),
        name=result.get("name", body.name),
        url=result.get("url", body.url),
    )


@mcp_router.delete("/servers/{server_id}", status_code=204)
@limiter.limit("10/minute")
async def delete_server(request: Request, server_id: str) -> None:
    """Remove a registered MCP server (admin only — scoped via RBAC)."""
    _require_auth(request)
    client = _require_gateway()
    resp = await client._http.delete(
        f"/gateways/{server_id}",
        headers=client._auth_headers(),
    )
    if resp.status_code == 404:
        raise HTTPException(status_code=404, detail="Server not found")
    resp.raise_for_status()
