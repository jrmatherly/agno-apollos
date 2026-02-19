"""Health endpoint tests."""


def test_health_endpoint(backend_url, session):
    """Backend health check returns 200."""
    r = session.get(f"{backend_url}/health")
    assert r.status_code == 200


def test_agents_list(backend_url, session):
    """Agents list endpoint returns registered agents."""
    r = session.get(f"{backend_url}/v1/agents")
    assert r.status_code == 200
    agents = r.json()
    agent_ids = [a["agent_id"] for a in agents]
    assert "knowledge-agent" in agent_ids
    assert "web-search-agent" in agent_ids
    assert "mcp-agent" in agent_ids
