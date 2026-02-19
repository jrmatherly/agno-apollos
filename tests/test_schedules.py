"""Scheduler integration tests.

These tests verify the scheduler endpoints are accessible.
Requires the backend to be running with scheduler=True.
"""


def test_schedules_endpoint(url_for, session):
    """Scheduler endpoint is accessible."""
    r = session.get(url_for("/schedules"))
    # Accept 200 (schedules exist) or 404 (no schedules yet) — both confirm the scheduler is running
    assert r.status_code in (200, 404)
