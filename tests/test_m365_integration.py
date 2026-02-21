"""
M365 integration tests — require running backend with M365_ENABLED=true.

Skipped by default in CI (M365_ENABLED not set). Run manually against a
live stack with Azure credentials configured.
"""

import os

import pytest

M365 = os.getenv("M365_ENABLED", "").lower() in ("true", "1", "yes")
pytestmark = pytest.mark.skipif(not M365, reason="M365_ENABLED not set")


def test_m365_status_endpoint_exists(backend_url, session, url_for):
    """M365 status endpoint should be reachable when M365_ENABLED=true."""
    resp = session.get(url_for("/m365/status"))
    # 200 if authenticated, 401 if auth enabled but no token — either means endpoint exists
    assert resp.status_code in (200, 401)


def test_m365_connect_requires_auth(backend_url, session, url_for):
    """Connect endpoint should reject unauthenticated requests."""
    resp = session.post(url_for("/m365/connect"))
    assert resp.status_code == 401


def test_m365_agent_registered(backend_url, session, url_for):
    """M365 agent should appear in the agents list."""
    resp = session.get(url_for("/agents"))
    assert resp.status_code == 200
    agents = resp.json()
    ids = [a.get("agent_id") or a.get("id") for a in agents]
    assert "m365-agent" in ids
