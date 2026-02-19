"""Health endpoint tests."""


def test_health_endpoint(url_for, session):
    """Backend health check returns 200."""
    r = session.get(url_for("/health"))
    assert r.status_code == 200


def test_agents_list(url_for, session):
    """Agents list endpoint returns registered agents."""
    r = session.get(url_for("/agents"))
    assert r.status_code == 200
    agents = r.json()
    agent_ids = [a["agent_id"] for a in agents]
    assert "knowledge-agent" in agent_ids
    assert "web-search-agent" in agent_ids
    assert "mcp-agent" in agent_ids
