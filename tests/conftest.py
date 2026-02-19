"""Integration test fixtures.

NOTE: AgentOS registers routes WITHOUT a ``/v1/`` prefix.
Use the ``url_for`` fixture to build endpoint URLs so that the correct
base path is always used (and never accidentally prefixed with ``/v1``).
"""

import os
import time

import pytest
import requests

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
TIMEOUT = int(os.getenv("TEST_TIMEOUT", "60"))


@pytest.fixture(scope="session")
def backend_url():
    """Wait for backend to be healthy and return URL."""
    start = time.time()
    while time.time() - start < TIMEOUT:
        try:
            r = requests.get(f"{BACKEND_URL}/health")
            if r.status_code == 200:
                return BACKEND_URL
        except requests.ConnectionError:
            pass
        time.sleep(2)
    pytest.fail(f"Backend not ready after {TIMEOUT}s at {BACKEND_URL}")


@pytest.fixture(scope="session")
def session():
    """Requests session with retry logic."""
    s = requests.Session()
    adapter = requests.adapters.HTTPAdapter(max_retries=3)
    s.mount("http://", adapter)
    s.mount("https://", adapter)
    return s


@pytest.fixture(scope="session")
def url_for(backend_url):
    """Build an API URL from a path.

    AgentOS registers routes *without* a ``/v1/`` prefix.  Using this
    fixture instead of manual f-strings prevents the common mistake of
    copying ``/v1/`` from upstream Agno docs.

    Usage::

        def test_agents_list(url_for, session):
            r = session.get(url_for("/agents"))
    """

    def _url_for(path: str) -> str:
        clean = path.lstrip("/")
        if clean.startswith("v1/"):
            raise ValueError(
                f"Route must NOT include a /v1/ prefix (got '/{clean}'). "
                "AgentOS registers routes at the root."
            )
        return f"{backend_url}/{clean}"

    return _url_for
