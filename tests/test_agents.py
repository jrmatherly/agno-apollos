"""Agent integration tests.

These tests verify agents are registered and respond to basic queries.
Requires the backend to be running with a connected database.
"""


def test_knowledge_agent_responds(backend_url, session):
    """Knowledge agent accepts a run request."""
    r = session.post(
        f"{backend_url}/v1/agents/knowledge-agent/runs",
        json={"message": "What is Agno?", "stream": False},
    )
    assert r.status_code == 200


def test_web_search_agent_responds(backend_url, session):
    """Web search agent accepts a run request."""
    r = session.post(
        f"{backend_url}/v1/agents/web-search-agent/runs",
        json={"message": "What is Python?", "stream": False},
    )
    assert r.status_code == 200


def test_mcp_agent_responds(backend_url, session):
    """MCP agent accepts a run request."""
    r = session.post(
        f"{backend_url}/v1/agents/mcp-agent/runs",
        json={"message": "Hello", "stream": False},
    )
    assert r.status_code == 200
