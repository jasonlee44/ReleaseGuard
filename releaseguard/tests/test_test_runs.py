from unittest.mock import patch

import pytest

from app.services.test_run_service import (
    LATENCY_THRESHOLD_MS,
    PROBE_CONFIG,
    PROBE_DEVICE_ID,
    REGRESSION_CONFIG,
    SUITE_CASE_RUNNERS,
)


def _ok_response(body: dict, latency_ms: float = 1.5) -> dict:
    return {
        "status_code": 200,
        "latency_ms": latency_ms,
        "body": body,
        "error": None,
    }


def _status_body():
    return {
        "device_id": PROBE_DEVICE_ID,
        "online": True,
        "cpu_percent": 24.5,
        "memory_percent": 44.0,
        "last_seen": "2026-06-22T12:00:00Z",
    }


def _admin_ok(mode: str = "normal") -> dict:
    return _ok_response(
        {
            "mode": mode,
            "delay_ms": 2000,
            "error_rate": 0.3,
            "message": f"Fault mode set to {mode}",
        }
    )


def _happy_path_mocks():
    """Mocks for cases 1–6 succeeding; fault probes still need separate side effects."""
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
        "update_device_config.return_value": _ok_response(
            {
                "device_id": PROBE_DEVICE_ID,
                "config_version": 2,
                "config": PROBE_CONFIG,
            }
        ),
        "get_firmware_version.return_value": _ok_response(
            {
                "product": "ReleaseGuard Fake Router",
                "firmware_version": "2.4.1",
                "build_id": "router-api-v1.0",
            }
        ),
        "set_fault_mode.return_value": _admin_ok("slow"),
        "reset_fault_mode.return_value": _admin_ok("normal"),
    }


def _configure_full_suite_with_fault_failures(mock_client):
    """Happy path passes; fault cases observe bad product behavior (option A → fail)."""
    mock_client.configure_mock(**_happy_path_mocks())
    mock_client.get_device_status.side_effect = [
        _ok_response(_status_body()),  # device_status
        _ok_response(_status_body(), latency_ms=2200.0),  # slow_response
    ]
    mock_client.get_health.side_effect = [
        _ok_response({"status": "OK"}),  # health_check
        {
            "status_code": 500,
            "latency_ms": 2.0,
            "body": {"detail": "Internal server error"},
            "error": None,
        },  # error_prone_service
        {
            "status_code": 503,
            "latency_ms": 2.0,
            "body": {"detail": "Service unavailable"},
            "error": None,
        },  # down_service
    ]
    mock_client.update_device_config.side_effect = [
        _ok_response(
            {
                "device_id": PROBE_DEVICE_ID,
                "config_version": 2,
                "config": PROBE_CONFIG,
            }
        ),  # config_update
        _ok_response(
            {
                "device_id": PROBE_DEVICE_ID,
                "config_version": 3,
                "config": REGRESSION_CONFIG,
            }
        ),  # config_regression POST (lies)
    ]
    mock_client.get_device_config.side_effect = [
        _ok_response(
            {
                "device_id": PROBE_DEVICE_ID,
                "config_version": 1,
                "config": {
                    "hostname": "edge-01",
                    "vlan_ids": [10, 20],
                    "routing_enabled": True,
                },
            }
        ),  # device_config read
        _ok_response(
            {
                "device_id": PROBE_DEVICE_ID,
                "config_version": 1,
                "config": {
                    "hostname": "edge-01",
                    "vlan_ids": [10, 20],
                    "routing_enabled": True,
                },
            }
        ),  # config_regression GET (unchanged)
    ]


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
def test_full_suite_fails_release_when_fault_modes_break_slos(mock_client, client):
    _configure_full_suite_with_fault_failures(mock_client)
    build_id = _create_build(client)

    create_response = client.post("/test-runs", json={"build_id": build_id})
    assert create_response.status_code == 200
    created = create_response.json()
    assert created["build_id"] == build_id
    assert created["status"] == "failed"
    assert len(created["results"]) == 10
    assert "6/10 passed" in created["summary"]
    assert all(case["expected_result"] for case in created["results"])
    assert all(case["actual_result"] for case in created["results"])

    by_name = {case["test_name"]: case for case in created["results"]}
    for name in (
        "health_check",
        "devices_list",
        "device_status",
        "device_config",
        "config_update",
        "firmware_version",
    ):
        assert by_name[name]["passed"] is True

    assert by_name["slow_response"]["passed"] is False
    assert "exceeded threshold" in (by_name["slow_response"]["failure_reason"] or "")
    assert by_name["slow_response"]["latency_ms"] > LATENCY_THRESHOLD_MS

    assert by_name["error_prone_service"]["passed"] is False
    assert by_name["down_service"]["passed"] is False
    assert by_name["config_regression"]["passed"] is False
    assert "did not persist" in (by_name["config_regression"]["failure_reason"] or "")

    assert mock_client.set_fault_mode.call_count == 4
    # start-of-suite reset + 4 per-fault resets + end-of-suite reset
    assert mock_client.reset_fault_mode.call_count == 6

    expected_order = [
        "health_check",
        "devices_list",
        "device_status",
        "device_config",
        "config_update",
        "firmware_version",
        "slow_response",
        "error_prone_service",
        "down_service",
        "config_regression",
    ]
    assert [case["test_name"] for case in created["results"]] == expected_order

    get_response = client.get(f"/test-runs/{created['run_id']}")
    assert get_response.status_code == 200
    assert get_response.json()["status"] == "failed"

    list_response = client.get("/test-runs")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1


@patch("app.services.test_run_service.router_client")
def test_create_test_run_failed_when_happy_path_probes_fail(mock_client, client):
    mock_client.configure_mock(
        **{
            "get_health.side_effect": [
                {
                    "status_code": None,
                    "latency_ms": 10.0,
                    "body": None,
                    "error": "connection refused",
                },
                {
                    "status_code": None,
                    "latency_ms": 10.0,
                    "body": None,
                    "error": "connection refused",
                },
                {
                    "status_code": None,
                    "latency_ms": 10.0,
                    "body": None,
                    "error": "connection refused",
                },
            ],
            "get_devices.return_value": {
                "status_code": 503,
                "latency_ms": 2.0,
                "body": {"detail": "Service unavailable"},
                "error": None,
            },
            "get_device_status.side_effect": [
                {
                    "status_code": 503,
                    "latency_ms": 2.0,
                    "body": {"detail": "Service unavailable"},
                    "error": None,
                },
                {
                    "status_code": 503,
                    "latency_ms": 2.0,
                    "body": {"detail": "Service unavailable"},
                    "error": None,
                },
            ],
            "get_device_config.side_effect": [
                {
                    "status_code": 503,
                    "latency_ms": 2.0,
                    "body": {"detail": "Service unavailable"},
                    "error": None,
                },
                {
                    "status_code": 503,
                    "latency_ms": 2.0,
                    "body": {"detail": "Service unavailable"},
                    "error": None,
                },
            ],
            "update_device_config.side_effect": [
                {
                    "status_code": 503,
                    "latency_ms": 2.0,
                    "body": {"detail": "Service unavailable"},
                    "error": None,
                },
                {
                    "status_code": 503,
                    "latency_ms": 2.0,
                    "body": {"detail": "Service unavailable"},
                    "error": None,
                },
            ],
            "get_firmware_version.return_value": {
                "status_code": 503,
                "latency_ms": 2.0,
                "body": {"detail": "Service unavailable"},
                "error": None,
            },
            "set_fault_mode.return_value": _admin_ok("down"),
            "reset_fault_mode.return_value": _admin_ok("normal"),
        }
    )
    build_id = _create_build(client)

    response = client.post("/test-runs", json={"build_id": build_id})
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "failed"
    assert len(body["results"]) == 10
    assert body["results"][0]["failure_reason"] == "connection refused"
    assert mock_client.reset_fault_mode.call_count == 6


@patch("app.services.test_run_service.router_client")
def test_config_update_mismatch_fails_case(mock_client, client):
    _configure_full_suite_with_fault_failures(mock_client)
    # Override first update (config_update case) to echo wrong config
    mock_client.update_device_config.side_effect = [
        _ok_response(
            {
                "device_id": PROBE_DEVICE_ID,
                "config_version": 2,
                "config": {
                    "hostname": "wrong-host",
                    "vlan_ids": [1],
                    "routing_enabled": False,
                },
            }
        ),
        _ok_response(
            {
                "device_id": PROBE_DEVICE_ID,
                "config_version": 3,
                "config": REGRESSION_CONFIG,
            }
        ),
    ]
    build_id = _create_build(client)

    response = client.post("/test-runs", json={"build_id": build_id})
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "failed"
    update_case = next(
        case for case in body["results"] if case["test_name"] == "config_update"
    )
    assert update_case["passed"] is False
    assert "hostname" in (update_case["failure_reason"] or "")


def test_list_test_runs_empty(client):
    response = client.get("/test-runs")
    assert response.status_code == 200
    assert response.json() == []


def test_get_test_run_not_found(client):
    response = client.get("/test-runs/00000000-0000-0000-0000-000000000099")
    assert response.status_code == 404
    assert response.json()["detail"] == "Test run not found"


def test_suite_defines_ten_core_cases_in_order():
    assert len(SUITE_CASE_RUNNERS) == 10
    assert [fn.__name__ for fn in SUITE_CASE_RUNNERS] == [
        "_run_health_check_case",
        "_run_devices_list_case",
        "_run_device_status_case",
        "_run_device_config_case",
        "_run_config_update_case",
        "_run_firmware_version_case",
        "_run_slow_response_case",
        "_run_error_prone_case",
        "_run_down_service_case",
        "_run_config_regression_case",
    ]


@patch("app.services.test_run_service.router_client")
def test_full_suite_passes_when_slos_hold_under_fault_modes(mock_client, client):
    """Option A pass path: product still meets SLOs even while fault modes are on."""
    mock_client.configure_mock(**_happy_path_mocks())
    mock_client.get_device_status.side_effect = [
        _ok_response(_status_body()),  # device_status
        _ok_response(_status_body(), latency_ms=120.0),  # slow_response under threshold
    ]
    mock_client.get_health.side_effect = [
        _ok_response({"status": "OK"}),  # health_check
        _ok_response({"status": "OK"}),  # error_prone still healthy
        _ok_response({"status": "OK"}),  # down still healthy (resilient product)
    ]
    mock_client.update_device_config.side_effect = [
        _ok_response(
            {
                "device_id": PROBE_DEVICE_ID,
                "config_version": 2,
                "config": PROBE_CONFIG,
            }
        ),
        _ok_response(
            {
                "device_id": PROBE_DEVICE_ID,
                "config_version": 3,
                "config": REGRESSION_CONFIG,
            }
        ),
    ]
    mock_client.get_device_config.side_effect = [
        _ok_response(
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
        _ok_response(
            {
                "device_id": PROBE_DEVICE_ID,
                "config_version": 3,
                "config": REGRESSION_CONFIG,
            }
        ),  # config actually persisted
    ]

    build_id = _create_build(client)
    response = client.post("/test-runs", json={"build_id": build_id})
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "passed"
    assert body["summary"] == "10/10 passed"
    assert all(case["passed"] for case in body["results"])


@pytest.mark.integration
def test_live_fake_router_health_optional():
    """Skipped unless RUN_INTEGRATION=1 and fake-router is reachable."""
    import os

    if os.getenv("RUN_INTEGRATION") != "1":
        pytest.skip("Set RUN_INTEGRATION=1 with fake-router on FAKE_ROUTER_URL to run")

    from app.clients import router_client

    health = router_client.get_health()
    assert health["error"] is None
    assert health["status_code"] == 200
    assert health["body"]["status"] == "OK"
