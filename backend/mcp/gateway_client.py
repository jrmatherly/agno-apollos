"""Client for ContextForge MCP Gateway API.

Handles JWT token generation (with jti + exp per RC1 requirements) and
gateway registration/discovery.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import httpx
import jwt


class GatewayClient:
    """Manages communication with the ContextForge MCP Gateway."""

    def __init__(self, base_url: str, jwt_secret: str) -> None:
        self._base_url = base_url.rstrip("/")
        self._jwt_secret = jwt_secret
        self._http = httpx.AsyncClient(base_url=self._base_url, timeout=30)

    def create_service_token(self, subject: str = "apollos-backend") -> str:
        """Create a JWT for authenticating to the gateway.

        RC1 requires both ``jti`` and ``exp`` claims — tokens without
        these are rejected with 401.
        """
        return jwt.encode(
            {
                "sub": subject,
                "jti": str(uuid.uuid4()),
                "exp": datetime.now(timezone.utc) + timedelta(hours=1),
                "aud": "mcpgateway-api",
                "iss": "mcpgateway",
            },
            self._jwt_secret,
            algorithm="HS256",
        )

    def _auth_headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.create_service_token()}"}

    async def list_gateways(self) -> list[dict]:
        """List all registered upstream MCP servers."""
        resp = await self._http.get("/gateways", headers=self._auth_headers())
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

    async def delete_gateway(self, gateway_id: str) -> bool:
        """Delete a registered gateway by ID. Returns False if not found."""
        resp = await self._http.delete(f"/gateways/{gateway_id}", headers=self._auth_headers())
        if resp.status_code == 404:
            return False
        resp.raise_for_status()
        return True

    async def close(self) -> None:
        await self._http.aclose()
