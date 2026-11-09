import pytest
from fastapi.testclient import TestClient

from app.data import builds, test_runs
from app.main import app


@pytest.fixture(scope="function")
def client():
    with TestClient(app) as test_client:
        builds.reset_builds()
        test_runs.reset_test_runs()
        yield test_client
