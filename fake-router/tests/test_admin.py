"""Tests for POST /admin/fault-mode.

Verify mode switching, option handling, and reset back to normal.
"""

def test_set_fault_mode_normal(client):
    response = client.post("/admin/fault-mode", json={"mode": "normal"})

    assert response.status_code == 200
    assert response.json()["mode"] == "normal"


def test_set_fault_mode_slow(client):
    response = client.post("/admin/fault-mode", json={"mode": "slow"})

    assert response.status_code == 200
    assert response.json()["mode"] == "slow"


def test_set_delay_ms(client):
    response = client.post("/admin/fault-mode", json={"mode": "slow", "delay_ms": 500})

    assert response.status_code == 200
    assert response.json()["mode"] == "slow"
    assert response.json()["delay_ms"] == 500


def test_set_fault_mode_error_prone(client):
    response = client.post("/admin/fault-mode", json={"mode": "error_prone"})

    assert response.status_code == 200
    assert response.json()["mode"] == "error_prone"


def test_set_error_rate(client):
    response = client.post("/admin/fault-mode", json={"mode": "error_prone", "error_rate": 1.0})

    assert response.status_code == 200
    assert response.json()["mode"] == "error_prone"
    assert response.json()["error_rate"] == 1.0
