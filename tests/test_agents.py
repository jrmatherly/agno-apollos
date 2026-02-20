"""Agent integration tests.

These tests verify agents are registered and respond to basic queries.
Requires the backend to be running with a connected database.
"""


def test_knowledge_agent_responds(url_for, session):
    """Knowledge agent accepts a run request."""
    r = session.post(
        url_for("/agents/knowledge-agent/runs"),
        data={"message": "What is Agno?", "stream": "false"},
    )
    assert r.status_code == 200


def test_web_search_agent_responds(url_for, session):
    """Web search agent accepts a run request."""
    r = session.post(
        url_for("/agents/web-search-agent/runs"),
        data={"message": "What is Python?", "stream": "false"},
    )
    assert r.status_code == 200


def test_mcp_agent_responds(url_for, session):
    """MCP agent accepts a run request."""
    r = session.post(
        url_for("/agents/mcp-agent/runs"),
        data={"message": "Hello", "stream": "false"},
    )
    assert r.status_code == 200
