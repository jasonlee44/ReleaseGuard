"""Tests for GET /health.

Verify normal responses, latency under fault modes, and expected
status codes when the service is in down or error_prone mode.
"""

import time


def test_health_returns_ok(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "OK"}


def test_health_returns_503_when_down(client):
    response = client.post("/admin/fault-mode", json={"mode": "down"})

    assert response.status_code == 200
    assert response.json()["mode"] == "down"

    response = client.get("/health")
    assert response.status_code == 503


def test_health_returns_ok_when_slow(client):
    TIME_DELAY = 400

    response = client.post("/admin/fault-mode", json={"mode": "slow", "delay_ms": TIME_DELAY})

    assert response.status_code == 200
    assert response.json()["mode"] == "slow"


    start = time.perf_counter()
    response = client.get("/health")
    end = time.perf_counter()

    assert response.status_code == 200
    assert (end - start) >= TIME_DELAY / 1000


def test_health_when_error_prone(client):
    response = client.post("/admin/fault-mode", json={"mode": "error_prone", "error_rate": 0.0})

    assert response.status_code == 200
    assert response.json()["mode"] == "error_prone"

    response = client.get("/health")
    assert response.status_code == 200


    response = client.post("/admin/fault-mode", json={"mode": "error_prone", "error_rate": 1.0})

    assert response.status_code == 200
    assert response.json()["mode"] == "error_prone"

    response = client.get("/health")
    assert response.status_code == 500
