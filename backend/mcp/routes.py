"""MCP Gateway proxy routes.

Thin proxy to the ContextForge gateway API, mounted at ``/mcp/`` on base_app
when ``MCP_GATEWAY_ENABLED=true``.

Gateways (registered upstream MCP servers):
  GET    /mcp/servers               List registered MCP servers
  GET    /mcp/servers/{id}          Get a single server
  POST   /mcp/servers               Register a new server
  PUT    /mcp/servers/{id}          Update server properties
  DELETE /mcp/servers/{id}          Remove a server
  POST   /mcp/servers/{id}/state    Enable/disable a server
  POST   /mcp/servers/{id}/refresh  Trigger tool re-discovery

Tools:
  GET    /mcp/tools                 List tools
  GET    /mcp/tools/{id}            Get a tool
  POST   /mcp/tools                 Create a tool
  PUT    /mcp/tools/{id}            Update a tool
  DELETE /mcp/tools/{id}            Delete a tool
  POST   /mcp/tools/{id}/state      Enable/disable a tool

Virtual Servers:
  GET    /mcp/virtual-servers               List virtual servers
  GET    /mcp/virtual-servers/{id}          Get a virtual server
  POST   /mcp/virtual-servers               Create a virtual server
  PUT    /mcp/virtual-servers/{id}          Update a virtual server
  DELETE /mcp/virtual-servers/{id}          Delete a virtual server
  POST   /mcp/virtual-servers/{id}/state    Enable/disable
  GET    /mcp/virtual-servers/{id}/tools     List tools in virtual server
  GET    /mcp/virtual-servers/{id}/resources List resources in virtual server
  GET    /mcp/virtual-servers/{id}/prompts   List prompts in virtual server

Resources:
  GET    /mcp/resources                  List resources
  GET    /mcp/resources/templates        List resource templates
  GET    /mcp/resources/{id}             Get a resource
  GET    /mcp/resources/{id}/info        Get resource metadata
  POST   /mcp/resources                  Create a resource
  PUT    /mcp/resources/{id}             Update a resource
  DELETE /mcp/resources/{id}             Delete a resource
  POST   /mcp/resources/{id}/state       Enable/disable a resource

Prompts:
  GET    /mcp/prompts                    List prompts
  GET    /mcp/prompts/{id}               Get a prompt
  POST   /mcp/prompts                    Create a prompt
  PUT    /mcp/prompts/{id}               Update a prompt
  DELETE /mcp/prompts/{id}               Delete a prompt
  POST   /mcp/prompts/{id}/state         Enable/disable a prompt

Tags:
  GET    /mcp/tags                       List tags (any authenticated)
  GET    /mcp/tags/{name}                Get tag entities (any authenticated)

Import/Export:
  GET    /mcp/export                     Export configuration
  POST   /mcp/import                     Import configuration
  GET    /mcp/import/status/{id}         Check import status

Health:
  GET    /mcp/health                     Gateway health (no auth)

Preferences:
  GET    /mcp/preferences                Get user preferences
  PUT    /mcp/preferences                Update user preferences
"""

from __future__ import annotations

import logging
from typing import NoReturn

import httpx
from fastapi import APIRouter, HTTPException, Request

from backend.auth.routes import limiter
from backend.mcp.config import get_gateway_client
from backend.mcp.schemas import (
    MCPHealthResponse,
    MCPImportRequest,
    MCPImportResponse,
    MCPPromptCreate,
    MCPPromptInfo,
    MCPPromptUpdate,
    MCPResourceCreate,
    MCPResourceInfo,
    MCPResourceUpdate,
    MCPServerInfo,
    MCPServerRegister,
    MCPServerResponse,
    MCPServerUpdate,
    MCPStateToggle,
    MCPTagInfo,
    MCPToolCreate,
    MCPToolInfo,
    MCPToolUpdate,
    MCPUserPreferences,
    MCPVirtualServerCreate,
    MCPVirtualServerInfo,
    MCPVirtualServerUpdate,
)
from backend.mcp.validation import URLValidationError, validate_mcp_server_url

log = logging.getLogger(__name__)

mcp_router = APIRouter(prefix="/mcp", tags=["mcp"])


# ── Helpers ──────────────────────────────────────────────────────────────


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


def _handle_gateway_error(
    exc: httpx.HTTPStatusError | httpx.ConnectError | httpx.TimeoutException,
) -> NoReturn:
    """Convert ContextForge HTTP errors to meaningful proxy responses."""
    if isinstance(exc, (httpx.ConnectError, httpx.TimeoutException)):
        log.error("Gateway connection error: %s", exc)
        raise HTTPException(status_code=502, detail="MCP Gateway unreachable") from exc

    status = exc.response.status_code
    try:
        body = exc.response.json()
        detail = body.get("detail", str(exc)) if isinstance(body, dict) else str(body)
    except (ValueError, UnicodeDecodeError):
        detail = exc.response.text or str(exc)

    log.error("Gateway error: status=%d detail=%s", status, detail)

    if status in (401, 403):
        raise HTTPException(status_code=502, detail=f"Gateway auth error: {detail}") from exc
    elif status == 404:
        raise HTTPException(status_code=404, detail=detail) from exc
    elif status == 409:
        raise HTTPException(status_code=409, detail=detail) from exc
    elif status == 422:
        raise HTTPException(status_code=422, detail=detail) from exc
    elif status == 429:
        raise HTTPException(status_code=429, detail=detail) from exc
    raise HTTPException(status_code=502, detail=f"Gateway error ({status}): {detail}") from exc


# ── Gateways (registered upstream MCP servers) ──────────────────────────


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
    gw = await client.get_gateway(server_id)
    if not gw:
        raise HTTPException(status_code=404, detail="Server not found")
    return MCPServerInfo(
        id=gw.get("id", server_id),
        name=gw.get("name", ""),
        url=gw.get("url", ""),
        status=gw.get("status"),
    )


@mcp_router.post("/servers", response_model=MCPServerResponse, status_code=201)
@limiter.limit("10/minute")
async def register_server(request: Request, body: MCPServerRegister) -> MCPServerResponse:
    """Register a new upstream MCP server."""
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


@mcp_router.put("/servers/{server_id}", response_model=MCPServerInfo)
@limiter.limit("10/minute")
async def update_server(request: Request, server_id: str, body: MCPServerUpdate) -> MCPServerInfo:
    """Update a registered MCP server's properties."""
    _require_auth(request)
    client = _require_gateway()
    try:
        result = await client.update_gateway(server_id, body.model_dump(exclude_none=True))
    except (httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException) as exc:
        _handle_gateway_error(exc)
    return MCPServerInfo(
        id=result.get("id", server_id),
        name=result.get("name", ""),
        url=result.get("url", ""),
        status=result.get("status"),
    )


@mcp_router.delete("/servers/{server_id}", status_code=204)
@limiter.limit("10/minute")
async def delete_server(request: Request, server_id: str) -> None:
    """Remove a registered MCP server."""
    _require_auth(request)
    client = _require_gateway()
    found = await client.delete_gateway(server_id)
    if not found:
        raise HTTPException(status_code=404, detail="Server not found")


@mcp_router.post("/servers/{server_id}/state")
@limiter.limit("10/minute")
async def toggle_server(request: Request, server_id: str, body: MCPStateToggle) -> dict:
    """Enable or disable a registered MCP server."""
    _require_auth(request)
    client = _require_gateway()
    try:
        return await client.toggle_gateway(server_id, activate=body.activate)
    except (httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException) as exc:
        _handle_gateway_error(exc)
        return {}  # unreachable — _handle_gateway_error always raises


@mcp_router.post("/servers/{server_id}/refresh")
@limiter.limit("10/minute")
async def refresh_server(request: Request, server_id: str) -> dict:
    """Trigger tool re-discovery for a registered MCP server."""
    _require_auth(request)
    client = _require_gateway()
    try:
        return await client.refresh_gateway(server_id)
    except (httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException) as exc:
        _handle_gateway_error(exc)
        return {}


# ── Tools ────────────────────────────────────────────────────────────────


@mcp_router.get("/tools", response_model=list[MCPToolInfo])
@limiter.limit("30/minute")
async def list_tools(
    request: Request,
    gateway_id: str | None = None,
    include_inactive: bool = False,
) -> list[MCPToolInfo]:
    """List tools from the gateway."""
    _require_auth(request)
    client = _require_gateway()
    tools = await client.list_tools(gateway_id=gateway_id, include_inactive=include_inactive)
    return [MCPToolInfo.model_validate(t) for t in tools]


@mcp_router.get("/tools/{tool_id}", response_model=MCPToolInfo)
@limiter.limit("30/minute")
async def get_tool(request: Request, tool_id: str) -> MCPToolInfo:
    """Get a specific tool."""
    _require_auth(request)
    client = _require_gateway()
    t = await client.get_tool(tool_id)
    if not t:
        raise HTTPException(status_code=404, detail="Tool not found")
    return MCPToolInfo.model_validate(t)


@mcp_router.post("/tools", response_model=MCPToolInfo, status_code=201)
@limiter.limit("10/minute")
async def create_tool(request: Request, body: MCPToolCreate) -> MCPToolInfo:
    """Create a new tool."""
    _require_auth(request)
    client = _require_gateway()
    tool_data = body.model_dump(exclude={"team_id", "visibility"})
    try:
        result = await client.create_tool(tool_data, team_id=body.team_id, visibility=body.visibility)
    except (httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException) as exc:
        _handle_gateway_error(exc)
    return MCPToolInfo.model_validate(result)


@mcp_router.put("/tools/{tool_id}", response_model=MCPToolInfo)
@limiter.limit("10/minute")
async def update_tool(request: Request, tool_id: str, body: MCPToolUpdate) -> MCPToolInfo:
    """Update a tool."""
    _require_auth(request)
    client = _require_gateway()
    try:
        result = await client.update_tool(tool_id, body.model_dump(exclude_none=True))
    except (httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException) as exc:
        _handle_gateway_error(exc)
    return MCPToolInfo.model_validate(result)


@mcp_router.delete("/tools/{tool_id}", status_code=204)
@limiter.limit("10/minute")
async def delete_tool(request: Request, tool_id: str) -> None:
    """Delete a tool."""
    _require_auth(request)
    client = _require_gateway()
    try:
        found = await client.delete_tool(tool_id)
    except (httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException) as exc:
        _handle_gateway_error(exc)
    if not found:
        raise HTTPException(status_code=404, detail="Tool not found")


@mcp_router.post("/tools/{tool_id}/state")
@limiter.limit("10/minute")
async def toggle_tool(request: Request, tool_id: str, body: MCPStateToggle) -> dict:
    """Enable or disable a tool."""
    _require_auth(request)
    client = _require_gateway()
    try:
        return await client.toggle_tool(tool_id, activate=body.activate)
    except (httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException) as exc:
        _handle_gateway_error(exc)
        return {}


# ── Virtual Servers ──────────────────────────────────────────────────────


@mcp_router.get("/virtual-servers", response_model=list[MCPVirtualServerInfo])
@limiter.limit("30/minute")
async def list_virtual_servers(
    request: Request,
    include_inactive: bool = False,
) -> list[MCPVirtualServerInfo]:
    """List virtual servers."""
    _require_auth(request)
    client = _require_gateway()
    servers = await client.list_virtual_servers(include_inactive=include_inactive)
    return [MCPVirtualServerInfo.model_validate(s) for s in servers]


@mcp_router.get("/virtual-servers/{vs_id}", response_model=MCPVirtualServerInfo)
@limiter.limit("30/minute")
async def get_virtual_server(request: Request, vs_id: str) -> MCPVirtualServerInfo:
    """Get a specific virtual server."""
    _require_auth(request)
    client = _require_gateway()
    s = await client.get_virtual_server(vs_id)
    if not s:
        raise HTTPException(status_code=404, detail="Virtual server not found")
    return MCPVirtualServerInfo.model_validate(s)


@mcp_router.post("/virtual-servers", response_model=MCPVirtualServerInfo, status_code=201)
@limiter.limit("10/minute")
async def create_virtual_server(request: Request, body: MCPVirtualServerCreate) -> MCPVirtualServerInfo:
    """Create a virtual server."""
    _require_auth(request)
    client = _require_gateway()
    server_data = body.model_dump(exclude={"team_id", "visibility"})
    try:
        result = await client.create_virtual_server(server_data, team_id=body.team_id, visibility=body.visibility)
    except (httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException) as exc:
        _handle_gateway_error(exc)
    return MCPVirtualServerInfo.model_validate(result)


@mcp_router.put("/virtual-servers/{vs_id}", response_model=MCPVirtualServerInfo)
@limiter.limit("10/minute")
async def update_virtual_server(request: Request, vs_id: str, body: MCPVirtualServerUpdate) -> MCPVirtualServerInfo:
    """Update a virtual server."""
    _require_auth(request)
    client = _require_gateway()
    try:
        result = await client.update_virtual_server(vs_id, body.model_dump(exclude_none=True))
    except (httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException) as exc:
        _handle_gateway_error(exc)
    return MCPVirtualServerInfo.model_validate(result)


@mcp_router.delete("/virtual-servers/{vs_id}", status_code=204)
@limiter.limit("10/minute")
async def delete_virtual_server(request: Request, vs_id: str) -> None:
    """Delete a virtual server."""
    _require_auth(request)
    client = _require_gateway()
    try:
        found = await client.delete_virtual_server(vs_id)
    except (httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException) as exc:
        _handle_gateway_error(exc)
    if not found:
        raise HTTPException(status_code=404, detail="Virtual server not found")


@mcp_router.post("/virtual-servers/{vs_id}/state")
@limiter.limit("10/minute")
async def toggle_virtual_server(request: Request, vs_id: str, body: MCPStateToggle) -> dict:
    """Enable or disable a virtual server."""
    _require_auth(request)
    client = _require_gateway()
    try:
        return await client.toggle_virtual_server(vs_id, activate=body.activate)
    except (httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException) as exc:
        _handle_gateway_error(exc)
        return {}


@mcp_router.get("/virtual-servers/{vs_id}/tools", response_model=list[MCPToolInfo])
@limiter.limit("30/minute")
async def list_virtual_server_tools(request: Request, vs_id: str) -> list[MCPToolInfo]:
    """List tools assigned to a virtual server."""
    _require_auth(request)
    client = _require_gateway()
    tools = await client.list_virtual_server_tools(vs_id)
    return [MCPToolInfo.model_validate(t) for t in tools]


@mcp_router.get("/virtual-servers/{vs_id}/resources", response_model=list[MCPResourceInfo])
@limiter.limit("30/minute")
async def list_virtual_server_resources(request: Request, vs_id: str) -> list[MCPResourceInfo]:
    """List resources assigned to a virtual server."""
    _require_auth(request)
    client = _require_gateway()
    resources = await client.list_virtual_server_resources(vs_id)
    return [MCPResourceInfo.model_validate(r) for r in resources]


@mcp_router.get("/virtual-servers/{vs_id}/prompts", response_model=list[MCPPromptInfo])
@limiter.limit("30/minute")
async def list_virtual_server_prompts(request: Request, vs_id: str) -> list[MCPPromptInfo]:
    """List prompts assigned to a virtual server."""
    _require_auth(request)
    client = _require_gateway()
    prompts = await client.list_virtual_server_prompts(vs_id)
    return [MCPPromptInfo.model_validate(p) for p in prompts]


# ── Resources ────────────────────────────────────────────────────────────


@mcp_router.get("/resources", response_model=list[MCPResourceInfo])
@limiter.limit("30/minute")
async def list_resources(
    request: Request,
    include_inactive: bool = False,
) -> list[MCPResourceInfo]:
    """List resources."""
    _require_auth(request)
    client = _require_gateway()
    resources = await client.list_resources(include_inactive=include_inactive)
    return [MCPResourceInfo.model_validate(r) for r in resources]


@mcp_router.get("/resources/templates")
@limiter.limit("30/minute")
async def list_resource_templates(request: Request) -> list[dict]:
    """List resource templates."""
    _require_auth(request)
    client = _require_gateway()
    return await client.list_resource_templates()


@mcp_router.get("/resources/{resource_id}", response_model=MCPResourceInfo)
@limiter.limit("30/minute")
async def get_resource(request: Request, resource_id: str) -> MCPResourceInfo:
    """Get a specific resource."""
    _require_auth(request)
    client = _require_gateway()
    r = await client.get_resource(resource_id)
    if not r:
        raise HTTPException(status_code=404, detail="Resource not found")
    return MCPResourceInfo.model_validate(r)


@mcp_router.get("/resources/{resource_id}/info")
@limiter.limit("30/minute")
async def get_resource_info(request: Request, resource_id: str) -> dict:
    """Get resource metadata."""
    _require_auth(request)
    client = _require_gateway()
    info = await client.get_resource_info(resource_id)
    if not info:
        raise HTTPException(status_code=404, detail="Resource not found")
    return info


@mcp_router.post("/resources", response_model=MCPResourceInfo, status_code=201)
@limiter.limit("10/minute")
async def create_resource(request: Request, body: MCPResourceCreate) -> MCPResourceInfo:
    """Create a resource."""
    _require_auth(request)
    client = _require_gateway()
    resource_data = body.model_dump(exclude={"team_id", "visibility"})
    try:
        result = await client.create_resource(resource_data, team_id=body.team_id, visibility=body.visibility)
    except (httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException) as exc:
        _handle_gateway_error(exc)
    return MCPResourceInfo.model_validate(result)


@mcp_router.put("/resources/{resource_id}", response_model=MCPResourceInfo)
@limiter.limit("10/minute")
async def update_resource(request: Request, resource_id: str, body: MCPResourceUpdate) -> MCPResourceInfo:
    """Update a resource."""
    _require_auth(request)
    client = _require_gateway()
    try:
        result = await client.update_resource(resource_id, body.model_dump(exclude_none=True))
    except (httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException) as exc:
        _handle_gateway_error(exc)
    return MCPResourceInfo.model_validate(result)


@mcp_router.delete("/resources/{resource_id}", status_code=204)
@limiter.limit("10/minute")
async def delete_resource(request: Request, resource_id: str) -> None:
    """Delete a resource."""
    _require_auth(request)
    client = _require_gateway()
    try:
        found = await client.delete_resource(resource_id)
    except (httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException) as exc:
        _handle_gateway_error(exc)
    if not found:
        raise HTTPException(status_code=404, detail="Resource not found")


@mcp_router.post("/resources/{resource_id}/state")
@limiter.limit("10/minute")
async def toggle_resource(request: Request, resource_id: str, body: MCPStateToggle) -> dict:
    """Enable or disable a resource."""
    _require_auth(request)
    client = _require_gateway()
    try:
        return await client.toggle_resource(resource_id, activate=body.activate)
    except (httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException) as exc:
        _handle_gateway_error(exc)
        return {}


# ── Prompts ──────────────────────────────────────────────────────────────


@mcp_router.get("/prompts", response_model=list[MCPPromptInfo])
@limiter.limit("30/minute")
async def list_prompts(
    request: Request,
    include_inactive: bool = False,
) -> list[MCPPromptInfo]:
    """List prompts."""
    _require_auth(request)
    client = _require_gateway()
    prompts = await client.list_prompts(include_inactive=include_inactive)
    return [MCPPromptInfo.model_validate(p) for p in prompts]


@mcp_router.get("/prompts/{prompt_id}", response_model=MCPPromptInfo)
@limiter.limit("30/minute")
async def get_prompt(request: Request, prompt_id: str) -> MCPPromptInfo:
    """Get a specific prompt."""
    _require_auth(request)
    client = _require_gateway()
    p = await client.get_prompt(prompt_id)
    if not p:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return MCPPromptInfo.model_validate(p)


@mcp_router.post("/prompts", response_model=MCPPromptInfo, status_code=201)
@limiter.limit("10/minute")
async def create_prompt(request: Request, body: MCPPromptCreate) -> MCPPromptInfo:
    """Create a prompt."""
    _require_auth(request)
    client = _require_gateway()
    prompt_data = body.model_dump(exclude={"team_id", "visibility"})
    try:
        result = await client.create_prompt(prompt_data, team_id=body.team_id, visibility=body.visibility)
    except (httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException) as exc:
        _handle_gateway_error(exc)
    return MCPPromptInfo.model_validate(result)


@mcp_router.put("/prompts/{prompt_id}", response_model=MCPPromptInfo)
@limiter.limit("10/minute")
async def update_prompt(request: Request, prompt_id: str, body: MCPPromptUpdate) -> MCPPromptInfo:
    """Update a prompt."""
    _require_auth(request)
    client = _require_gateway()
    try:
        result = await client.update_prompt(prompt_id, body.model_dump(exclude_none=True))
    except (httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException) as exc:
        _handle_gateway_error(exc)
    return MCPPromptInfo.model_validate(result)


@mcp_router.delete("/prompts/{prompt_id}", status_code=204)
@limiter.limit("10/minute")
async def delete_prompt(request: Request, prompt_id: str) -> None:
    """Delete a prompt."""
    _require_auth(request)
    client = _require_gateway()
    try:
        found = await client.delete_prompt(prompt_id)
    except (httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException) as exc:
        _handle_gateway_error(exc)
    if not found:
        raise HTTPException(status_code=404, detail="Prompt not found")


@mcp_router.post("/prompts/{prompt_id}/state")
@limiter.limit("10/minute")
async def toggle_prompt(request: Request, prompt_id: str, body: MCPStateToggle) -> dict:
    """Enable or disable a prompt."""
    _require_auth(request)
    client = _require_gateway()
    try:
        return await client.toggle_prompt(prompt_id, activate=body.activate)
    except (httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException) as exc:
        _handle_gateway_error(exc)
        return {}


# ── Tags ─────────────────────────────────────────────────────────────────


@mcp_router.get("/tags", response_model=list[MCPTagInfo])
@limiter.limit("30/minute")
async def list_tags(request: Request, entity_types: str | None = None) -> list[MCPTagInfo]:
    """List tags with usage statistics. Available to any authenticated user."""
    _require_auth(request)
    client = _require_gateway()
    tags = await client.list_tags(entity_types=entity_types)
    return [MCPTagInfo.model_validate(t) for t in tags]


@mcp_router.get("/tags/{tag_name}")
@limiter.limit("30/minute")
async def get_tag_entities(request: Request, tag_name: str, entity_types: str | None = None) -> dict:
    """Get entities associated with a tag."""
    _require_auth(request)
    client = _require_gateway()
    return await client.get_tag_entities(tag_name, entity_types=entity_types)


# ── Import/Export ────────────────────────────────────────────────────────


@mcp_router.get("/export")
@limiter.limit("10/minute")
async def export_config(
    request: Request,
    types: str | None = None,
    tags: str | None = None,
    include_inactive: bool = False,
    include_dependencies: bool = True,
) -> dict:
    """Export gateway configuration with optional filters."""
    _require_auth(request)
    client = _require_gateway()
    return await client.export_config(
        types=types,
        tags=tags,
        include_inactive=include_inactive,
        include_dependencies=include_dependencies,
    )


@mcp_router.post("/import", response_model=MCPImportResponse)
@limiter.limit("10/minute")
async def import_config(request: Request, body: MCPImportRequest) -> MCPImportResponse:
    """Import gateway configuration. Validates gateway URLs before forwarding."""
    _require_auth(request)
    client = _require_gateway()

    # Validate any gateway URLs in import data
    gateways = body.data.get("gateways", [])
    for gw in gateways:
        gw_url = gw.get("url")
        if gw_url:
            try:
                validate_mcp_server_url(gw_url, allow_internal=True)
            except URLValidationError as exc:
                raise HTTPException(
                    status_code=422,
                    detail=f"Invalid gateway URL in import: {exc}",
                ) from exc

    try:
        result = await client.import_config(
            body.data,
            conflict_strategy=body.conflict_strategy,
            dry_run=body.dry_run,
        )
    except (httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException) as exc:
        _handle_gateway_error(exc)
    return MCPImportResponse(
        import_id=result.get("import_id"),
        status=result.get("status", "completed"),
        summary=result.get("summary", {}),
    )


@mcp_router.get("/import/status/{import_id}")
@limiter.limit("30/minute")
async def get_import_status(request: Request, import_id: str) -> dict:
    """Check the status of a config import."""
    _require_auth(request)
    client = _require_gateway()
    return await client.get_import_status(import_id)


# ── Health ───────────────────────────────────────────────────────────────


@mcp_router.get("/health", response_model=MCPHealthResponse)
@limiter.limit("30/minute")
async def gateway_health(request: Request) -> MCPHealthResponse:
    """Gateway health check. No authentication required."""
    client = _require_gateway()
    try:
        health = await client.health()
        version_info = await client.version()
    except (httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException) as exc:
        raise HTTPException(status_code=502, detail="Gateway unreachable") from exc
    return MCPHealthResponse(
        status=health.get("status", "unknown"),
        version=version_info.get("version"),
    )


# ── Preferences ──────────────────────────────────────────────────────────


@mcp_router.get("/preferences", response_model=MCPUserPreferences)
@limiter.limit("30/minute")
async def get_preferences(request: Request) -> MCPUserPreferences:
    """Get MCP workspace preferences for the authenticated user."""
    from backend.auth.database import auth_session_factory
    from backend.mcp.preferences import get_preferences

    user_id = _require_auth(request)
    async with auth_session_factory() as session:
        return await get_preferences(session, user_id)


@mcp_router.put("/preferences", response_model=MCPUserPreferences)
@limiter.limit("10/minute")
async def update_preferences(request: Request, body: MCPUserPreferences) -> MCPUserPreferences:
    """Update MCP workspace preferences for the authenticated user."""
    from backend.auth.database import auth_session_factory
    from backend.mcp.preferences import save_preferences

    user_id = _require_auth(request)
    try:
        async with auth_session_factory() as session:
            await save_preferences(session, user_id, body)
    except ValueError:
        raise HTTPException(status_code=404, detail="User profile not synced yet")
    return body
