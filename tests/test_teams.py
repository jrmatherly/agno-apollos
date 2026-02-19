"""Team integration tests.

These tests verify teams are registered and can coordinate responses.
Requires the backend to be running with a connected database.
"""


def test_teams_list(url_for, session):
    """Teams list endpoint returns registered teams."""
    r = session.get(url_for("/teams"))
    assert r.status_code == 200
    teams = r.json()
    team_ids = [t["team_id"] for t in teams]
    assert "research-team" in team_ids


def test_research_team_responds(url_for, session):
    """Research team accepts a run request."""
    r = session.post(
        url_for("/teams/research-team/runs"),
        json={"message": "What are the benefits of multi-agent systems?", "stream": False},
    )
    assert r.status_code == 200
