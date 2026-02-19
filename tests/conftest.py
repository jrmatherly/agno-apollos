"""Integration test fixtures."""

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
