"""Client for ContextForge MCP Gateway API.

Handles JWT token generation (with jti + exp per RC1 requirements) and
full CRUD for gateways, tools, virtual servers, resources, prompts,
tags, import/export, and health.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING

import httpx
import jwt

if TYPE_CHECKING:
    from backend.mcp.schemas import MCPVisibility


class GatewayClient:
    """Manages communication with the ContextForge MCP Gateway."""

    def __init__(self, base_url: str, jwt_secret: str) -> None:
        self._base_url = base_url.rstrip("/")
        self._jwt_secret = jwt_secret
        self._http = httpx.AsyncClient(base_url=self._base_url, timeout=30)

    def create_service_token(self, user_id: str | None = None) -> str:
        """Create a service JWT for gateway authentication.

        Args:
            user_id: Optional Entra oid for audit trail (not used for auth).

        Note:
            is_admin=True + teams=None enables admin bypass in ContextForge's
            two-layer RBAC. Without these, all API calls get PUBLIC-ONLY
            visibility, silently filtering out team and private resources.
        """
        payload: dict[str, object] = {
            "sub": "apollos-backend",
            "jti": str(uuid.uuid4()),
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
            "aud": "mcpgateway-api",
            "iss": "mcpgateway",
            "is_admin": True,
            "teams": None,
        }
        if user_id:
            payload["user_id"] = user_id
        return jwt.encode(payload, self._jwt_secret, algorithm="HS256")

    def _auth_headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.create_service_token()}"}

    # ── Gateways ──────────────────────────────────────────────────────

    async def list_gateways(self) -> list[dict]:
        """List all registered upstream MCP servers.

        Passes limit=0 to fetch all items. ContextForge defaults to 50-item
        limit when no limit is specified, causing silent data truncation.
        """
        resp = await self._http.get("/gateways", headers=self._auth_headers(), params={"limit": "0"})
        resp.raise_for_status()
        return resp.json()

    async def get_server_id_by_name(self, name: str) -> str | None:
        """Look up a registered server's ID by its name."""
        gateways = await self.list_gateways()
        for gw in gateways:
            if gw.get("name") == name:
                return gw.get("id")
        return None

    def get_server_mcp_url(self, server_id: str) -> str:
        """Get the MCP endpoint URL for a registered server."""
        return f"{self._base_url}/servers/{server_id}/mcp"

    async def get_gateway(self, gateway_id: str) -> dict | None:
        """Get a single registered gateway by ID. Returns None if not found."""
        resp = await self._http.get(f"/gateways/{gateway_id}", headers=self._auth_headers())
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()

    async def register_gateway(self, name: str, url: str) -> dict:
        """Register an upstream MCP server with the gateway."""
        resp = await self._http.post(
            "/gateways",
            headers={**self._auth_headers(), "Content-Type": "application/json"},
            json={"name": name, "url": url},
        )
        resp.raise_for_status()
        return resp.json()

    async def update_gateway(self, gateway_id: str, data: dict) -> dict:
        """Update a registered gateway's properties.

        Note: Gateways use flat JSON (single Pydantic model, no multi-Body wrapping).
        """
        resp = await self._http.put(f"/gateways/{gateway_id}", headers=self._auth_headers(), json=data)
        resp.raise_for_status()
        return resp.json()

    async def toggle_gateway(self, gateway_id: str, *, activate: bool) -> dict:
        """Enable or disable a gateway.

        Note: activate is a query parameter, not a request body.
        ContextForge signature: set_gateway_state(gateway_id, activate: bool = True)
        """
        resp = await self._http.post(
            f"/gateways/{gateway_id}/state",
            headers=self._auth_headers(),
            params={"activate": str(activate).lower()},
        )
        resp.raise_for_status()
        return resp.json()

    async def refresh_gateway(
        self, gateway_id: str, *, include_resources: bool = True, include_prompts: bool = True
    ) -> dict:
        """Trigger re-discovery of tools/resources/prompts from a gateway."""
        resp = await self._http.post(
            f"/gateways/{gateway_id}/tools/refresh",
            headers=self._auth_headers(),
            params={
                "include_resources": str(include_resources).lower(),
                "include_prompts": str(include_prompts).lower(),
            },
        )
        resp.raise_for_status()
        return resp.json()

    async def delete_gateway(self, gateway_id: str) -> bool:
        """Delete a registered gateway by ID. Returns False if not found."""
        resp = await self._http.delete(f"/gateways/{gateway_id}", headers=self._auth_headers())
        if resp.status_code == 404:
            return False
        resp.raise_for_status()
        return True

    # ── Tools ─────────────────────────────────────────────────────────

    async def list_tools(
        self, *, gateway_id: str | None = None, tags: list[str] | None = None, include_inactive: bool = False
    ) -> list[dict]:
        """List tools, optionally filtered by gateway or tags.

        Passes limit=0 to fetch all items (ContextForge defaults to 50).
        """
        params: dict[str, str] = {"limit": "0"}
        if gateway_id:
            params["gateway_id"] = gateway_id
        if tags:
            params["tags"] = ",".join(tags)
        if include_inactive:
            params["include_inactive"] = "true"
        resp = await self._http.get("/tools", headers=self._auth_headers(), params=params)
        resp.raise_for_status()
        return resp.json()

    async def get_tool(self, tool_id: str) -> dict | None:
        """Get a single tool by ID. Returns None if not found."""
        resp = await self._http.get(f"/tools/{tool_id}", headers=self._auth_headers())
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()

    async def create_tool(
        self, tool_data: dict, *, team_id: str | None = None, visibility: MCPVisibility = "public"
    ) -> dict:
        """Register a tool.

        IMPORTANT: Body must be wrapped as {"tool": {...}, "team_id": "...", "visibility": "..."}
        because ContextForge's POST /tools has multiple Body() parameters.
        """
        body: dict[str, object] = {"tool": tool_data, "visibility": visibility}
        if team_id:
            body["team_id"] = team_id
        resp = await self._http.post("/tools", headers=self._auth_headers(), json=body)
        resp.raise_for_status()
        return resp.json()

    async def update_tool(self, tool_id: str, tool_data: dict, *, team_id: str | None = None) -> dict:
        """Update a tool's properties.

        Body wrapped as {"tool": {...}, "team_id": "..."} for safety.
        ContextForge PUT /tools/{id} may have multi-Body params — verify at runtime.
        """
        body: dict[str, object] = {"tool": tool_data}
        if team_id:
            body["team_id"] = team_id
        resp = await self._http.put(f"/tools/{tool_id}", headers=self._auth_headers(), json=body)
        resp.raise_for_status()
        return resp.json()

    async def toggle_tool(self, tool_id: str, *, activate: bool) -> dict:
        """Enable or disable a tool. activate is a query parameter."""
        resp = await self._http.post(
            f"/tools/{tool_id}/state",
            headers=self._auth_headers(),
            params={"activate": str(activate).lower()},
        )
        resp.raise_for_status()
        return resp.json()

    async def delete_tool(self, tool_id: str) -> bool:
        """Delete a tool. Returns False if not found."""
        resp = await self._http.delete(f"/tools/{tool_id}", headers=self._auth_headers())
        if resp.status_code == 404:
            return False
        resp.raise_for_status()
        return True

    # ── Virtual Servers (ContextForge 'servers') ──────────────────────

    async def list_virtual_servers(self, *, include_inactive: bool = False) -> list[dict]:
        """List virtual servers (ContextForge 'servers' — tool/resource/prompt compositions).

        Passes limit=0 to fetch all items (ContextForge defaults to 50).
        """
        params: dict[str, str] = {"limit": "0"}
        if include_inactive:
            params["include_inactive"] = "true"
        resp = await self._http.get("/servers", headers=self._auth_headers(), params=params)
        resp.raise_for_status()
        return resp.json()

    async def get_virtual_server(self, server_id: str) -> dict | None:
        resp = await self._http.get(f"/servers/{server_id}", headers=self._auth_headers())
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()

    async def create_virtual_server(
        self, server_data: dict, *, team_id: str | None = None, visibility: MCPVisibility = "public"
    ) -> dict:
        """Create a virtual server.

        Body wrapped as {"server": {...}, "team_id": "...", "visibility": "..."} because
        ContextForge's POST /servers has multiple Body() parameters.
        """
        body: dict[str, object] = {"server": server_data, "visibility": visibility}
        if team_id:
            body["team_id"] = team_id
        resp = await self._http.post("/servers", headers=self._auth_headers(), json=body)
        resp.raise_for_status()
        return resp.json()

    async def update_virtual_server(self, server_id: str, server_data: dict, *, team_id: str | None = None) -> dict:
        """Update a virtual server. Body wrapped for safety."""
        body: dict[str, object] = {"server": server_data}
        if team_id:
            body["team_id"] = team_id
        resp = await self._http.put(f"/servers/{server_id}", headers=self._auth_headers(), json=body)
        resp.raise_for_status()
        return resp.json()

    async def toggle_virtual_server(self, server_id: str, *, activate: bool) -> dict:
        resp = await self._http.post(
            f"/servers/{server_id}/state",
            headers=self._auth_headers(),
            params={"activate": str(activate).lower()},
        )
        resp.raise_for_status()
        return resp.json()

    async def delete_virtual_server(self, server_id: str) -> bool:
        resp = await self._http.delete(f"/servers/{server_id}", headers=self._auth_headers())
        if resp.status_code == 404:
            return False
        resp.raise_for_status()
        return True

    async def list_virtual_server_tools(self, server_id: str) -> list[dict]:
        resp = await self._http.get(f"/servers/{server_id}/tools", headers=self._auth_headers())
        resp.raise_for_status()
        return resp.json()

    async def list_virtual_server_resources(self, server_id: str) -> list[dict]:
        resp = await self._http.get(f"/servers/{server_id}/resources", headers=self._auth_headers())
        resp.raise_for_status()
        return resp.json()

    async def list_virtual_server_prompts(self, server_id: str) -> list[dict]:
        resp = await self._http.get(f"/servers/{server_id}/prompts", headers=self._auth_headers())
        resp.raise_for_status()
        return resp.json()

    # ── Resources ─────────────────────────────────────────────────────

    async def list_resources(self, *, include_inactive: bool = False) -> list[dict]:
        """List resources. Passes limit=0 to fetch all items (ContextForge defaults to 50)."""
        params: dict[str, str] = {"limit": "0"}
        if include_inactive:
            params["include_inactive"] = "true"
        resp = await self._http.get("/resources", headers=self._auth_headers(), params=params)
        resp.raise_for_status()
        return resp.json()

    async def get_resource(self, resource_id: str) -> dict | None:
        resp = await self._http.get(f"/resources/{resource_id}", headers=self._auth_headers())
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()

    async def get_resource_info(self, resource_id: str) -> dict | None:
        """Get resource metadata only (not content)."""
        resp = await self._http.get(f"/resources/{resource_id}/info", headers=self._auth_headers())
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()

    async def create_resource(
        self, resource_data: dict, *, team_id: str | None = None, visibility: MCPVisibility = "public"
    ) -> dict:
        """Create a resource. Body wrapped as {"resource": {...}, ...}."""
        body: dict[str, object] = {"resource": resource_data, "visibility": visibility}
        if team_id:
            body["team_id"] = team_id
        resp = await self._http.post("/resources", headers=self._auth_headers(), json=body)
        resp.raise_for_status()
        return resp.json()

    async def update_resource(self, resource_id: str, resource_data: dict, *, team_id: str | None = None) -> dict:
        body: dict[str, object] = {"resource": resource_data}
        if team_id:
            body["team_id"] = team_id
        resp = await self._http.put(f"/resources/{resource_id}", headers=self._auth_headers(), json=body)
        resp.raise_for_status()
        return resp.json()

    async def toggle_resource(self, resource_id: str, *, activate: bool) -> dict:
        resp = await self._http.post(
            f"/resources/{resource_id}/state",
            headers=self._auth_headers(),
            params={"activate": str(activate).lower()},
        )
        resp.raise_for_status()
        return resp.json()

    async def delete_resource(self, resource_id: str) -> bool:
        resp = await self._http.delete(f"/resources/{resource_id}", headers=self._auth_headers())
        if resp.status_code == 404:
            return False
        resp.raise_for_status()
        return True

    async def list_resource_templates(self) -> list[dict]:
        """List resource templates. Path: /resources/templates/list"""
        resp = await self._http.get("/resources/templates/list", headers=self._auth_headers())
        resp.raise_for_status()
        return resp.json()

    # ── Prompts ───────────────────────────────────────────────────────

    async def list_prompts(self, *, include_inactive: bool = False) -> list[dict]:
        """List prompts. Passes limit=0 to fetch all items (ContextForge defaults to 50)."""
        params: dict[str, str] = {"limit": "0"}
        if include_inactive:
            params["include_inactive"] = "true"
        resp = await self._http.get("/prompts", headers=self._auth_headers(), params=params)
        resp.raise_for_status()
        return resp.json()

    async def get_prompt(self, prompt_id: str) -> dict | None:
        resp = await self._http.get(f"/prompts/{prompt_id}", headers=self._auth_headers())
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()

    async def create_prompt(
        self, prompt_data: dict, *, team_id: str | None = None, visibility: MCPVisibility = "public"
    ) -> dict:
        """Create a prompt. Body wrapped as {"prompt": {...}, ...}."""
        body: dict[str, object] = {"prompt": prompt_data, "visibility": visibility}
        if team_id:
            body["team_id"] = team_id
        resp = await self._http.post("/prompts", headers=self._auth_headers(), json=body)
        resp.raise_for_status()
        return resp.json()

    async def update_prompt(self, prompt_id: str, prompt_data: dict, *, team_id: str | None = None) -> dict:
        body: dict[str, object] = {"prompt": prompt_data}
        if team_id:
            body["team_id"] = team_id
        resp = await self._http.put(f"/prompts/{prompt_id}", headers=self._auth_headers(), json=body)
        resp.raise_for_status()
        return resp.json()

    async def toggle_prompt(self, prompt_id: str, *, activate: bool) -> dict:
        resp = await self._http.post(
            f"/prompts/{prompt_id}/state",
            headers=self._auth_headers(),
            params={"activate": str(activate).lower()},
        )
        resp.raise_for_status()
        return resp.json()

    async def delete_prompt(self, prompt_id: str) -> bool:
        resp = await self._http.delete(f"/prompts/{prompt_id}", headers=self._auth_headers())
        if resp.status_code == 404:
            return False
        resp.raise_for_status()
        return True

    # ── Tags (read-only) ──────────────────────────────────────────────

    async def list_tags(self, *, entity_types: str | None = None) -> list[dict]:
        """List tags. Returns [{name, stats: {tools, resources, ...}, entities: [...]}].

        Passes limit=0 to fetch all items (ContextForge defaults to 50).
        """
        params: dict[str, str] = {"limit": "0"}
        if entity_types:
            params["entity_types"] = entity_types
        resp = await self._http.get("/tags", headers=self._auth_headers(), params=params)
        resp.raise_for_status()
        return resp.json()

    async def get_tag_entities(self, tag_name: str, *, entity_types: str | None = None) -> dict:
        params: dict[str, str] = {}
        if entity_types:
            params["entity_types"] = entity_types
        resp = await self._http.get(f"/tags/{tag_name}/entities", headers=self._auth_headers(), params=params)
        resp.raise_for_status()
        return resp.json()

    # ── Import / Export ───────────────────────────────────────────────

    async def export_config(
        self,
        *,
        types: str | None = None,
        tags: str | None = None,
        include_inactive: bool = False,
        include_dependencies: bool = True,
    ) -> dict:
        """Export gateway configuration with optional filters."""
        params: dict[str, str] = {}
        if types:
            params["types"] = types
        if tags:
            params["tags"] = tags
        if include_inactive:
            params["include_inactive"] = "true"
        if not include_dependencies:
            params["include_dependencies"] = "false"
        resp = await self._http.get("/export", headers=self._auth_headers(), params=params)
        resp.raise_for_status()
        return resp.json()

    async def import_config(self, data: dict, *, conflict_strategy: str = "update", dry_run: bool = False) -> dict:
        """Import gateway configuration.

        Note: ContextForge defaults conflict_strategy to "update", not "skip".
        """
        resp = await self._http.post(
            "/import",
            headers=self._auth_headers(),
            json=data,
            params={
                "conflict_strategy": conflict_strategy,
                "dry_run": str(dry_run).lower(),
            },
        )
        resp.raise_for_status()
        return resp.json()

    async def get_import_status(self, import_id: str) -> dict:
        resp = await self._http.get(f"/import/status/{import_id}", headers=self._auth_headers())
        resp.raise_for_status()
        return resp.json()

    # ── Health (no auth required) ─────────────────────────────────────

    async def health(self) -> dict:
        resp = await self._http.get("/health")
        resp.raise_for_status()
        return resp.json()

    async def version(self) -> dict:
        resp = await self._http.get("/version")
        resp.raise_for_status()
        return resp.json()

    # ── Lifecycle ─────────────────────────────────────────────────────

    async def close(self) -> None:
        await self._http.aclose()
