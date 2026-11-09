from unittest.mock import patch

from app.services.test_run_service import PROBE_DEVICE_ID


def _ok_response(body: dict, latency_ms: float = 1.5) -> dict:
    return {
        "status_code": 200,
        "latency_ms": latency_ms,
        "body": body,
        "error": None,
    }


def _failing_probes():
    return {
        "get_health.return_value": {
            "status_code": None,
            "latency_ms": 10.0,
            "body": None,
            "error": "connection refused",
        },
        "get_devices.return_value": {
            "status_code": 503,
            "latency_ms": 2.0,
            "body": {"detail": "Service unavailable"},
            "error": None,
        },
        "get_device_status.return_value": {
            "status_code": 503,
            "latency_ms": 2.0,
            "body": {"detail": "Service unavailable"},
            "error": None,
        },
        "get_device_config.return_value": {
            "status_code": 503,
            "latency_ms": 2.0,
            "body": {"detail": "Service unavailable"},
            "error": None,
        },
        "get_firmware_version.return_value": {
            "status_code": 503,
            "latency_ms": 2.0,
            "body": {"detail": "Service unavailable"},
            "error": None,
        },
    }


def _passing_probes():
    return {
        "get_health.return_value": _ok_response({"status": "OK"}),
        "get_devices.return_value": _ok_response(
            {
                "devices": [
                    {"device_id": "router-001", "type": "edge-router", "online": True}
                ],
                "count": 1,
            }
        ),
        "get_device_status.return_value": _ok_response(
            {
                "device_id": PROBE_DEVICE_ID,
                "online": True,
                "cpu_percent": 24.5,
                "memory_percent": 44.0,
                "last_seen": "2026-06-22T12:00:00Z",
            }
        ),
        "get_device_config.return_value": _ok_response(
            {
                "device_id": PROBE_DEVICE_ID,
                "config_version": 1,
                "config": {
                    "hostname": "edge-01",
                    "vlan_ids": [10, 20],
                    "routing_enabled": True,
                },
            }
        ),
        "get_firmware_version.return_value": _ok_response(
            {
                "product": "ReleaseGuard Fake Router",
                "firmware_version": "2.4.1",
                "build_id": "router-api-v1.0",
            }
        ),
    }


def _create_build(client) -> str:
    response = client.post(
        "/builds",
        json={"name": "build-01", "version": "01", "description": "test"},
    )
    assert response.status_code == 200
    return response.json()["build_id"]


@patch("app.services.test_run_service.router_client")
def test_create_test_run_missing_build(mock_client, client):
    response = client.post(
        "/test-runs",
        json={"build_id": "00000000-0000-0000-0000-000000000001"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Build not found"
    mock_client.get_health.assert_not_called()


@patch("app.services.test_run_service.router_client")
def test_create_and_get_passing_test_run(mock_client, client):
    mock_client.configure_mock(**_passing_probes())
    build_id = _create_build(client)

    create_response = client.post("/test-runs", json={"build_id": build_id})
    assert create_response.status_code == 200
    created = create_response.json()
    assert created["build_id"] == build_id
    assert created["status"] == "passed"
    assert len(created["results"]) == 5
    assert all(case["passed"] for case in created["results"])
    assert {case["test_name"] for case in created["results"]} == {
        "health_check",
        "devices_list",
        "device_status",
        "device_config",
        "firmware_version",
    }

    get_response = client.get(f"/test-runs/{created['run_id']}")
    assert get_response.status_code == 200
    assert get_response.json()["run_id"] == created["run_id"]
    assert get_response.json()["status"] == "passed"


@patch("app.services.test_run_service.router_client")
def test_create_test_run_failed_when_probes_fail(mock_client, client):
    mock_client.configure_mock(**_failing_probes())
    build_id = _create_build(client)

    response = client.post("/test-runs", json={"build_id": build_id})
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "failed"
    assert len(body["results"]) == 5
    assert all(not case["passed"] for case in body["results"])
    assert body["results"][0]["failure_reason"] == "connection refused"


def test_get_test_run_not_found(client):
    response = client.get("/test-runs/00000000-0000-0000-0000-000000000099")
    assert response.status_code == 404
    assert response.json()["detail"] == "Test run not found"
