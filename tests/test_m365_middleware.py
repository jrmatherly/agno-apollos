"""Tests for M365 token propagation middleware."""

from unittest.mock import MagicMock, patch

from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import PlainTextResponse, Response
from starlette.routing import Route
from starlette.testclient import TestClient

from backend.auth.m365_middleware import M365TokenMiddleware
from backend.tools.m365 import _current_graph_token


def _make_app() -> tuple[Starlette, list[str]]:
    """Create a minimal Starlette app that captures the graph token during requests."""
    captured: list[str] = []

    async def capture_token(request: Request) -> PlainTextResponse:
        captured.append(_current_graph_token.get())
        return PlainTextResponse("ok")

    app = Starlette(routes=[Route("/test", capture_token)])
    app.add_middleware(M365TokenMiddleware)
    return app, captured


class _FakeAuthMiddleware(BaseHTTPMiddleware):
    """Simulates EntraJWTMiddleware by setting request.state fields."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request.state.authenticated = True
        request.state.user_id = "test-oid"
        return await call_next(request)


def test_middleware_sets_graph_token_for_authenticated_user():
    """Middleware should set graph token when user is authenticated and has M365 connection."""
    app, captured = _make_app()
    app.add_middleware(_FakeAuthMiddleware)

    mock_service = MagicMock()
    mock_service.get_graph_token.return_value = "graph-token-xyz"

    with patch("backend.auth.m365_token_service.get_obo_service", return_value=mock_service):
        resp = TestClient(app).get("/test")

    assert resp.status_code == 200
    assert captured[-1] == "graph-token-xyz"


def test_middleware_clears_token_after_request():
    """Graph token should be cleared after request completes (no leakage)."""
    assert _current_graph_token.get() == ""


def test_middleware_skips_unauthenticated_requests():
    """Middleware should not attempt token lookup for unauthenticated requests."""
    app, captured = _make_app()

    resp = TestClient(app).get("/test")
    assert resp.status_code == 200
    assert captured[-1] == ""


def test_middleware_handles_no_graph_token():
    """Middleware should not set token when user has no M365 connection."""
    app, captured = _make_app()
    app.add_middleware(_FakeAuthMiddleware)

    mock_service = MagicMock()
    mock_service.get_graph_token.return_value = None

    with patch("backend.auth.m365_token_service.get_obo_service", return_value=mock_service):
        resp = TestClient(app).get("/test")

    assert resp.status_code == 200
    assert captured[-1] == ""
