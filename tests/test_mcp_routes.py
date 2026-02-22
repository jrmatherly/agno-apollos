"""Unit tests for MCP proxy routes."""

from __future__ import annotations

import asyncio
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from backend.mcp.routes import (
    _handle_gateway_error,
    _require_auth,
    _require_gateway,
)


def _run(coro):
    """Helper to run async code in sync tests."""
    return asyncio.get_event_loop().run_until_complete(coro)


# ── Helper Tests ─────────────────────────────────────────────────────────


class TestRequireAuth:
    def test_raises_401_when_not_authenticated(self):
        request = MagicMock()
        request.state = MagicMock(spec=[])
        with pytest.raises(HTTPException) as exc_info:
            _require_auth(request)
        assert exc_info.value.status_code == 401

    def test_raises_401_when_no_user_id(self):
        request = MagicMock()
        request.state.authenticated = True
        request.state.user_id = None
        with pytest.raises(HTTPException) as exc_info:
            _require_auth(request)
        assert exc_info.value.status_code == 401

    def test_returns_user_id(self):
        request = MagicMock()
        request.state.authenticated = True
        request.state.user_id = "user-123"
        assert _require_auth(request) == "user-123"


class TestRequireGateway:
    def test_raises_503_when_no_client(self):
        with patch("backend.mcp.routes.get_gateway_client", return_value=None):
            with pytest.raises(HTTPException) as exc_info:
                _require_gateway()
            assert exc_info.value.status_code == 503


class TestHandleGatewayError:
    def _make_exc(self, status_code: int, detail: str = "err") -> Exception:
        resp = MagicMock()
        resp.status_code = status_code
        resp.json.return_value = {"detail": detail}
        import httpx

        return httpx.HTTPStatusError("test", request=MagicMock(), response=resp)

    def test_401_becomes_502(self):
        with pytest.raises(HTTPException) as exc_info:
            _handle_gateway_error(self._make_exc(401))
        assert exc_info.value.status_code == 502

    def test_404_passes_through(self):
        with pytest.raises(HTTPException) as exc_info:
            _handle_gateway_error(self._make_exc(404))
        assert exc_info.value.status_code == 404

    def test_409_passes_through(self):
        with pytest.raises(HTTPException) as exc_info:
            _handle_gateway_error(self._make_exc(409, "conflict"))
        assert exc_info.value.status_code == 409

    def test_422_passes_through(self):
        with pytest.raises(HTTPException) as exc_info:
            _handle_gateway_error(self._make_exc(422, "validation"))
        assert exc_info.value.status_code == 422

    def test_500_becomes_502(self):
        with pytest.raises(HTTPException) as exc_info:
            _handle_gateway_error(self._make_exc(500))
        assert exc_info.value.status_code == 502


# ── Route Pattern Tests ──────────────────────────────────────────────────


class TestRoutePatterns:
    """Verify all routes follow the required patterns."""

    @staticmethod
    def _route_handlers():
        """Get all route handler functions defined in routes module."""
        import inspect

        from backend.mcp import routes

        for name, obj in inspect.getmembers(routes, inspect.isfunction):
            if name.startswith("_"):
                continue
            # Only check functions defined in routes.py itself
            if inspect.getmodule(obj) is not routes:
                continue
            yield name, obj

    def test_all_routes_use_require_auth_except_health(self):
        """Every route handler except health must call _require_auth."""
        import inspect

        for name, obj in self._route_handlers():
            if name == "gateway_health":
                continue
            source = inspect.getsource(obj)
            assert "_require_auth(request)" in source, f"Route {name} missing _require_auth"

    def test_all_gateway_routes_use_require_gateway(self):
        """Every gateway-proxied route handler must call _require_gateway."""
        import inspect

        # Preferences are local (file-based), not proxied through gateway
        skip = {"get_preferences", "update_preferences"}
        for name, obj in self._route_handlers():
            if name in skip:
                continue
            source = inspect.getsource(obj)
            assert "_require_gateway()" in source, f"Route {name} missing _require_gateway"

    def test_health_route_does_not_require_auth(self):
        """Health endpoint must NOT call _require_auth."""
        import inspect

        from backend.mcp import routes

        source = inspect.getsource(routes.gateway_health)
        assert "_require_auth" not in source


# ── Scope Mapper Tests ───────────────────────────────────────────────────


class TestScopeMapper:
    """Verify RBAC scope mappings are complete."""

    def test_all_7_previously_missing_routes_have_scopes(self):
        """HIGH-1 fix: verify all 7 previously missing routes are mapped."""
        from backend.auth.scope_mapper import get_required_scopes

        # These 7 were missing before the fix
        missing_routes = [
            ("PUT", "/mcp/servers/some-id"),
            ("POST", "/mcp/servers/some-id/state"),
            ("POST", "/mcp/servers/some-id/refresh"),
            ("GET", "/mcp/virtual-servers/some-id/tools"),
            ("GET", "/mcp/virtual-servers/some-id/resources"),
            ("GET", "/mcp/virtual-servers/some-id/prompts"),
            ("GET", "/mcp/resources/some-id/info"),
        ]
        for method, path in missing_routes:
            scopes = get_required_scopes(method, path)
            # Should NOT fall through to default admin scope
            assert scopes != ["agent_os:admin"], f"Route {method} {path} still falls through to admin default"

    def test_tags_scope_is_any_authenticated(self):
        """MEDIUM-5 fix: tags should be [] (any authenticated), not mcp:tools:read."""
        from backend.auth.scope_mapper import get_required_scopes

        assert get_required_scopes("GET", "/mcp/tags") == []
        assert get_required_scopes("GET", "/mcp/tags/some-tag") == []

    def test_health_scope_is_any_authenticated(self):
        from backend.auth.scope_mapper import get_required_scopes

        assert get_required_scopes("GET", "/mcp/health") == []

    def test_admin_has_all_mcp_scopes(self):
        """Admin role should have all MCP scopes."""
        from backend.auth.scope_mapper import ROLE_SCOPE_MAP

        admin_scopes = ROLE_SCOPE_MAP["Admin"]
        required = [
            "mcp:tools:read",
            "mcp:tools:write",
            "mcp:tools:delete",
            "mcp:virtual-servers:read",
            "mcp:virtual-servers:write",
            "mcp:virtual-servers:delete",
            "mcp:resources:read",
            "mcp:resources:write",
            "mcp:resources:delete",
            "mcp:prompts:read",
            "mcp:prompts:write",
            "mcp:prompts:delete",
            "mcp:config:read",
            "mcp:config:write",
            "mcp:preferences:read",
            "mcp:preferences:write",
        ]
        for scope in required:
            assert scope in admin_scopes, f"Admin missing scope: {scope}"

    def test_user_has_read_and_preference_scopes(self):
        """User role should have read + preferences but not write/delete."""
        from backend.auth.scope_mapper import ROLE_SCOPE_MAP

        user_scopes = ROLE_SCOPE_MAP["User"]
        # Should have
        assert "mcp:tools:read" in user_scopes
        assert "mcp:preferences:read" in user_scopes
        assert "mcp:preferences:write" in user_scopes
        # Should NOT have
        assert "mcp:tools:write" not in user_scopes
        assert "mcp:tools:delete" not in user_scopes
        assert "mcp:config:write" not in user_scopes

    def test_devops_has_config_read(self):
        """DevOps should have config:read for monitoring."""
        from backend.auth.scope_mapper import ROLE_SCOPE_MAP

        assert "mcp:config:read" in ROLE_SCOPE_MAP["DevOps"]


# ── Preferences Tests ────────────────────────────────────────────────────


class TestPreferences:
    def test_default_preferences(self):
        from backend.mcp.preferences import get_preferences

        prefs = get_preferences("nonexistent-user")
        assert prefs.default_tab == "servers"
        assert prefs.hidden_tools == []
        assert prefs.compact_view is False

    def test_save_and_load(self, tmp_path):
        from backend.mcp.preferences import get_preferences, save_preferences

        with patch("backend.mcp.preferences._PREFS_DIR", tmp_path):
            prefs = MagicMock()
            prefs.model_dump_json.return_value = (
                '{"hidden_tools": ["t1"], "hidden_servers": [], "default_tab": "tools", "compact_view": true}'
            )

            save_preferences("user-1", prefs)
            loaded = get_preferences("user-1")
            assert loaded.hidden_tools == ["t1"]
            assert loaded.default_tab == "tools"
            assert loaded.compact_view is True

    def test_safe_filename(self):
        from backend.mcp.preferences import _prefs_path

        path = _prefs_path("user@example.com/../../etc")
        assert ".." not in path.name
        assert "/" not in path.name
