"""Tests for M365 MCP tools layer — contextvars-based header_provider."""

from unittest.mock import MagicMock


def test_m365_tools_imports():
    from backend.tools.m365 import m365_header_provider, m365_mcp_tools

    assert callable(m365_mcp_tools)
    assert callable(m365_header_provider)


def test_header_provider_returns_empty_when_no_token():
    from backend.tools.m365 import _current_graph_token, m365_header_provider

    _current_graph_token.set("")
    mock_ctx = MagicMock()
    mock_ctx.user_id = "test-user"
    result = m365_header_provider(mock_ctx)
    assert result == {}


def test_header_provider_returns_bearer_when_token_set():
    from backend.tools.m365 import _current_graph_token, m365_header_provider

    _current_graph_token.set("graph-token-abc")
    mock_ctx = MagicMock()
    mock_ctx.user_id = "test-user"
    result = m365_header_provider(mock_ctx)
    assert result == {"Authorization": "Bearer graph-token-abc"}
    # Clean up
    _current_graph_token.set("")


def test_set_and_clear_graph_token():
    from backend.tools.m365 import _current_graph_token, clear_graph_token, set_graph_token

    set_graph_token("my-token")
    assert _current_graph_token.get() == "my-token"
    clear_graph_token()
    assert _current_graph_token.get() == ""


def test_m365_mcp_tools_returns_empty_when_disabled(monkeypatch):
    monkeypatch.setenv("M365_ENABLED", "false")
    from backend.tools.m365 import m365_mcp_tools

    result = m365_mcp_tools()
    assert result == []
