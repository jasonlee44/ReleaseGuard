"""Shared pytest fixtures for Fake Router Service tests.

Provide a TestClient for the FastAPI app, reset fault mode and device state between tests.
"""

import pytest
from fastapi.testclient import TestClient

from app.data import seed
from app.fault import state
from app.main import app


@pytest.fixture(scope="function")
def client():
    """HTTP client with fault mode and device seed reset per test."""
    with TestClient(app) as test_client: # 'with' runs startup/shutdown cleanly
        state.reset_fault_state()
        seed.reset_devices()
        yield test_client # 'yield' gives the client to the test, then runs cleanup after test finishes
