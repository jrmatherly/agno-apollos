"""Unit tests for GatewayClient."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import jwt as pyjwt
import pytest

from backend.mcp.gateway_client import GatewayClient


def _run(coro):
    """Helper to run async code in sync tests."""
    return asyncio.get_event_loop().run_until_complete(coro)


@pytest.fixture
def client():
    return GatewayClient(base_url="http://localhost:4444", jwt_secret="test-secret")


# ── Service Token ─────────────────────────────────────────────────────


class TestServiceToken:
    def test_service_token_has_required_claims(self, client):
        """Service JWT must include jti, exp, is_admin, and teams per ContextForge RBAC."""
        token = client.create_service_token()
        payload = pyjwt.decode(token, "test-secret", algorithms=["HS256"], audience="mcpgateway-api")
        assert "jti" in payload
        assert "exp" in payload
        assert payload["sub"] == "apollos-backend"
        assert payload["aud"] == "mcpgateway-api"
        assert payload["iss"] == "mcpgateway"
        assert payload["is_admin"] is True
        assert payload["teams"] is None

    def test_service_token_includes_user_id_when_provided(self, client):
        """user_id is embedded as audit claim, not for auth."""
        token = client.create_service_token(user_id="user-oid-123")
        payload = pyjwt.decode(token, "test-secret", algorithms=["HS256"], audience="mcpgateway-api")
        assert payload["user_id"] == "user-oid-123"

    def test_service_token_omits_user_id_when_none(self, client):
        """No user_id claim when not provided."""
        token = client.create_service_token()
        payload = pyjwt.decode(token, "test-secret", algorithms=["HS256"], audience="mcpgateway-api")
        assert "user_id" not in payload

    def test_auth_headers_uses_service_token(self, client):
        headers = client._auth_headers()
        assert "Authorization" in headers
        assert headers["Authorization"].startswith("Bearer ")


# ── Gateway Mutations ─────────────────────────────────────────────────


class TestGatewayMutations:
    def test_update_gateway(self, client):
        with patch.object(client._http, "put", new_callable=AsyncMock) as mock_put:
            mock_put.return_value = MagicMock(
                status_code=200,
                json=lambda: {"id": "gw-1", "name": "updated", "url": "http://example.com"},
                raise_for_status=lambda: None,
            )
            result = _run(client.update_gateway("gw-1", {"name": "updated"}))
            assert result["name"] == "updated"
            mock_put.assert_called_once()

    def test_toggle_gateway(self, client):
        with patch.object(client._http, "post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = MagicMock(
                status_code=200,
                json=lambda: {"id": "gw-1", "enabled": False},
                raise_for_status=lambda: None,
            )
            result = _run(client.toggle_gateway("gw-1", activate=False))
            assert result["enabled"] is False
            mock_post.assert_called_once()
            _, kwargs = mock_post.call_args
            assert kwargs["params"]["activate"] == "false"

    def test_refresh_gateway(self, client):
        with patch.object(client._http, "post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = MagicMock(
                status_code=200,
                json=lambda: {"tools_discovered": 5},
                raise_for_status=lambda: None,
            )
            result = _run(client.refresh_gateway("gw-1"))
            assert result["tools_discovered"] == 5


# ── Tool Methods ──────────────────────────────────────────────────────


class TestToolMethods:
    def test_create_tool_wraps_body(self, client):
        """POST /tools requires body wrapped in 'tool' key (multi-Body endpoint)."""
        with patch.object(client._http, "post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = MagicMock(
                status_code=201,
                json=lambda: {"id": "t-1", "name": "test"},
                raise_for_status=lambda: None,
            )
            _run(client.create_tool({"name": "test", "description": "A test tool"}, team_id="team-123"))
            _, kwargs = mock_post.call_args
            body = kwargs["json"]
            assert "tool" in body
            assert body["tool"]["name"] == "test"
            assert body["team_id"] == "team-123"

    def test_create_tool_without_team_id(self, client):
        """team_id omitted when None."""
        with patch.object(client._http, "post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = MagicMock(
                status_code=201,
                json=lambda: {"id": "t-1", "name": "test"},
                raise_for_status=lambda: None,
            )
            _run(client.create_tool({"name": "test"}))
            _, kwargs = mock_post.call_args
            body = kwargs["json"]
            assert "tool" in body
            assert "team_id" not in body

    def test_update_tool_wraps_body(self, client):
        """PUT /tools/{id} wraps body for safety."""
        with patch.object(client._http, "put", new_callable=AsyncMock) as mock_put:
            mock_put.return_value = MagicMock(
                status_code=200,
                json=lambda: {"id": "t-1", "name": "updated"},
                raise_for_status=lambda: None,
            )
            _run(client.update_tool("t-1", {"name": "updated"}, team_id="team-456"))
            _, kwargs = mock_put.call_args
            body = kwargs["json"]
            assert "tool" in body
            assert body["tool"]["name"] == "updated"

    def test_get_tool_returns_none_on_404(self, client):
        with patch.object(client._http, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = MagicMock(status_code=404)
            result = _run(client.get_tool("nonexistent"))
            assert result is None

    def test_delete_tool_returns_false_on_404(self, client):
        with patch.object(client._http, "delete", new_callable=AsyncMock) as mock_del:
            mock_del.return_value = MagicMock(status_code=404)
            result = _run(client.delete_tool("nonexistent"))
            assert result is False

    def test_toggle_tool_uses_query_param(self, client):
        with patch.object(client._http, "post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = MagicMock(
                status_code=200,
                json=lambda: {"id": "t-1", "is_active": True},
                raise_for_status=lambda: None,
            )
            _run(client.toggle_tool("t-1", activate=True))
            _, kwargs = mock_post.call_args
            assert kwargs["params"]["activate"] == "true"


# ── Virtual Server Methods ────────────────────────────────────────────


class TestVirtualServerMethods:
    def test_create_virtual_server_wraps_body(self, client):
        with patch.object(client._http, "post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = MagicMock(
                status_code=201,
                json=lambda: {"id": "vs-1", "name": "test-vs"},
                raise_for_status=lambda: None,
            )
            _run(client.create_virtual_server({"name": "test-vs"}, team_id="t1", visibility="team"))
            _, kwargs = mock_post.call_args
            body = kwargs["json"]
            assert "server" in body
            assert body["server"]["name"] == "test-vs"
            assert body["team_id"] == "t1"
            assert body["visibility"] == "team"

    def test_list_virtual_server_tools(self, client):
        with patch.object(client._http, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = MagicMock(
                status_code=200,
                json=lambda: [{"id": "tool-1"}],
                raise_for_status=lambda: None,
            )
            result = _run(client.list_virtual_server_tools("vs-1"))
            assert len(result) == 1


# ── Resource Methods ──────────────────────────────────────────────────


class TestResourceMethods:
    def test_create_resource_wraps_body(self, client):
        with patch.object(client._http, "post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = MagicMock(
                status_code=201,
                json=lambda: {"id": "r-1", "name": "test-res"},
                raise_for_status=lambda: None,
            )
            _run(client.create_resource({"name": "test-res"}, visibility="private"))
            _, kwargs = mock_post.call_args
            body = kwargs["json"]
            assert "resource" in body
            assert body["visibility"] == "private"
            assert "team_id" not in body


# ── Prompt Methods ────────────────────────────────────────────────────


class TestPromptMethods:
    def test_create_prompt_wraps_body(self, client):
        with patch.object(client._http, "post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = MagicMock(
                status_code=201,
                json=lambda: {"id": "p-1", "name": "test-prompt"},
                raise_for_status=lambda: None,
            )
            _run(client.create_prompt({"name": "test-prompt"}, team_id="t2"))
            _, kwargs = mock_post.call_args
            body = kwargs["json"]
            assert "prompt" in body
            assert body["team_id"] == "t2"


# ── Import/Export ─────────────────────────────────────────────────────


class TestImportExport:
    def test_import_config_defaults_to_update(self, client):
        """conflict_strategy defaults to 'update', not 'skip'."""
        with patch.object(client._http, "post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = MagicMock(
                status_code=200,
                json=lambda: {"status": "completed"},
                raise_for_status=lambda: None,
            )
            _run(client.import_config({"tools": []}))
            _, kwargs = mock_post.call_args
            assert kwargs["params"]["conflict_strategy"] == "update"

    def test_export_config_forwards_filters(self, client):
        with patch.object(client._http, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = MagicMock(
                status_code=200,
                json=lambda: {"tools": []},
                raise_for_status=lambda: None,
            )
            _run(client.export_config(types="tools", tags="ml", include_inactive=True))
            _, kwargs = mock_get.call_args
            assert kwargs["params"]["types"] == "tools"
            assert kwargs["params"]["tags"] == "ml"
            assert kwargs["params"]["include_inactive"] == "true"


# ── Health ────────────────────────────────────────────────────────────


class TestHealth:
    def test_health_no_auth(self, client):
        """Health endpoint does not send auth headers."""
        with patch.object(client._http, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = MagicMock(
                status_code=200,
                json=lambda: {"status": "ok"},
                raise_for_status=lambda: None,
            )
            result = _run(client.health())
            assert result["status"] == "ok"
            _, kwargs = mock_get.call_args
            assert "headers" not in kwargs
