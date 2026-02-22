"""Team integration tests.

These tests verify teams are registered and can coordinate responses.
Requires the backend to be running with a connected database.
"""


def test_teams_list(url_for, session):
    """Teams list endpoint returns registered teams."""
    r = session.get(url_for("/teams"))
    assert r.status_code == 200
    teams = r.json()
    team_ids = [t["id"] for t in teams]
    assert "research-team" in team_ids


def test_research_team_responds(url_for, session):
    """Research team accepts a run request."""
    r = session.post(
        url_for("/teams/research-team/runs"),
        data={"message": "What are the benefits of multi-agent systems?", "stream": "false"},
    )
    assert r.status_code == 200


def test_coordinator_team_listed(url_for, session):
    """Coordinator team appears in teams list."""
    r = session.get(url_for("/teams"))
    assert r.status_code == 200
    teams = r.json()
    team_ids = [t["id"] for t in teams]
    assert "apollos-coordinator" in team_ids


def test_coordinator_team_routes_query(url_for, session):
    """Coordinator team accepts a run and routes to a specialist."""
    r = session.post(
        url_for("/teams/apollos-coordinator/runs"),
        data={"message": "What documents are in the knowledge base?", "stream": "false"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data.get("content") is not None, "Coordinator should return a response"
