"""Tests for device inventory, status, and configuration endpoints.

Cover GET /devices, GET/POST /devices/{device_id}/status and config, including 
config_bug read/write mismatch detection scenarios.
"""

def test_get_devices_returns_three_devices(client):
    response = client.get("/devices")

    assert response.status_code == 200
    body = response.json()
    assert {"router-001", "router-002", "switch-001"} == {d["device_id"] for d in body["devices"]}
    assert body["count"] == 3


def test_get_device_status_for_known_id(client):
    response = client.get("/devices/router-001/status")

    assert response.status_code == 200
    assert response.json()["device_id"] == "router-001"


def test_get_device_status_returns_404_for_unknown_id(client):
    response = client.get("/devices/router-067/status")

    assert response.status_code == 404
    assert response.json()["detail"] == "Device with id router-067 not found."


def test_get_device_config_for_known_id(client):
    response = client.get("/devices/router-002/config")

    assert response.status_code == 200
    assert response.json()["device_id"] == "router-002"


def test_get_device_config_returns_404_for_unknown_id(client):
    response = client.get("/devices/router-069/config")

    assert response.status_code == 404
    assert response.json()["detail"] == "Device with id router-069 not found."


def test_update_config_changes_hostname(client):
    response = client.post(
        "/devices/router-001/config", 
        json={"config": {
            "hostname": "router-1", 
            "vlan_ids": [10, 20], 
            "routing_enabled": True
        }}
    )
    
    assert response.status_code == 200
    assert response.json()["config"]["hostname"] == "router-1"


    response = client.get("/devices/router-001/config")

    assert response.json()["config"]["hostname"] == "router-1"
    assert response.json()["config_version"] == 2


def test_update_config_not_change_under_config_bug(client):
    response = client.post("/admin/fault-mode", json={"mode": "config_bug"})

    assert response.status_code == 200
    assert response.json()["mode"] == "config_bug"


    response = client.post(
        "/devices/router-001/config",
        json={"config": {
            "hostname": "router-new-name",
            "vlan_ids": [10, 20],
            "routing_enabled": True
        }}
    )

    assert response.status_code == 200
    assert response.json()["config"]["hostname"] == "router-new-name"


    response = client.get("/devices/router-001/config")

    assert response.json()["config"]["hostname"] == "edge-01"