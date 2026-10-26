import pytest
from fastapi.testclient import TestClient

from app.data import builds
from app.main import app

@pytest.fixture(scope="function")
def client():
    with TestClient(app) as test_client:
        builds.reset_builds()
        yield test_client
