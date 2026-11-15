import os

os.environ["DATABASE_URL"] = ("postgresql+psycopg://jasonlee@localhost:5432/releaseguard_test")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.main import app
from app.db.database import SessionLocal, init_db


@pytest.fixture(scope="function")
def client():
    init_db()
    with SessionLocal() as session:
        session.execute(text("TRUNCATE test_case_results, test_runs, builds CASCADE"))
        session.commit()
    with TestClient(app) as test_client:
        yield test_client
