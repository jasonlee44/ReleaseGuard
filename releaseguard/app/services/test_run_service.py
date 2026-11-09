from datetime import datetime, timezone
from uuid import UUID, uuid4

from app.clients import router_client
from app.data.builds import BUILDS
from app.data.test_runs import TEST_RUNS
from app.schemas.test_run import TestCaseResult, TestRun, TestRunCreate

# Seeded device used for status/config checks against fake-router
PROBE_DEVICE_ID = "router-001"


def _transport_failure_reason(response: dict) -> str | None:
    if response["error"] is not None:
        return response["error"]
    if response["status_code"] != 200:
        return f"expected status 200, got {response['status_code']}"
    if response.get("body") is None:
        return "expected JSON body, got none"
    return None


def _evaluate_health(response: dict) -> tuple[bool, str | None]:
    reason = _transport_failure_reason(response)
    if reason is not None:
        return False, reason
    if response["body"].get("status") != "OK":
        return False, f"unexpected body: {response['body']!r}"
    return True, None


def _evaluate_devices_list(response: dict) -> tuple[bool, str | None]:
    reason = _transport_failure_reason(response)
    if reason is not None:
        return False, reason
    body = response["body"]
    devices = body.get("devices")
    count = body.get("count")
    if not isinstance(devices, list) or not isinstance(count, int):
        return False, f"unexpected body: {body!r}"
    if count < 1 or len(devices) != count:
        return False, f"expected non-empty device list matching count, got {body!r}"
    return True, None


def _evaluate_device_status(response: dict, device_id: str) -> tuple[bool, str | None]:
    reason = _transport_failure_reason(response)
    if reason is not None:
        return False, reason
    body = response["body"]
    if body.get("device_id") != device_id or "online" not in body:
        return False, f"unexpected body: {body!r}"
    return True, None


def _evaluate_device_config(response: dict, device_id: str) -> tuple[bool, str | None]:
    reason = _transport_failure_reason(response)
    if reason is not None:
        return False, reason
    body = response["body"]
    config = body.get("config")
    if body.get("device_id") != device_id or not isinstance(config, dict):
        return False, f"unexpected body: {body!r}"
    if "hostname" not in config or "vlan_ids" not in config:
        return False, f"unexpected config: {config!r}"
    return True, None


def _evaluate_firmware(response: dict) -> tuple[bool, str | None]:
    reason = _transport_failure_reason(response)
    if reason is not None:
        return False, reason
    body = response["body"]
    if not body.get("product") or not body.get("firmware_version"):
        return False, f"unexpected body: {body!r}"
    return True, None


def _run_case(test_name: str, endpoint: str, response: dict, passed: bool, failure_reason: str | None) -> TestCaseResult:
    return TestCaseResult(
        test_name=test_name,
        endpoint=endpoint,
        status_code=response["status_code"],
        latency_ms=response["latency_ms"],
        passed=passed,
        failure_reason=failure_reason,
    )


def create_test_run(payload: TestRunCreate) -> TestRun | None:
    # Cannot test a release we never registered
    if str(payload.build_id) not in BUILDS:
        return None

    started_at = datetime.now(timezone.utc)
    results: list[TestCaseResult] = []

    health = router_client.get_health()
    health_passed, health_reason = _evaluate_health(health)
    results.append(
        _run_case("health_check", "/health", health, health_passed, health_reason)
    )

    devices = router_client.get_devices()
    devices_passed, devices_reason = _evaluate_devices_list(devices)
    results.append(
        _run_case("devices_list", "/devices", devices, devices_passed, devices_reason)
    )

    status = router_client.get_device_status(PROBE_DEVICE_ID)
    status_passed, status_reason = _evaluate_device_status(status, PROBE_DEVICE_ID)
    results.append(
        _run_case(
            "device_status",
            f"/devices/{PROBE_DEVICE_ID}/status",
            status,
            status_passed,
            status_reason,
        )
    )

    config = router_client.get_device_config(PROBE_DEVICE_ID)
    config_passed, config_reason = _evaluate_device_config(config, PROBE_DEVICE_ID)
    results.append(
        _run_case(
            "device_config",
            f"/devices/{PROBE_DEVICE_ID}/config",
            config,
            config_passed,
            config_reason,
        )
    )

    firmware = router_client.get_firmware_version()
    firmware_passed, firmware_reason = _evaluate_firmware(firmware)
    results.append(
        _run_case(
            "firmware_version",
            "/firmware/version",
            firmware,
            firmware_passed,
            firmware_reason,
        )
    )

    completed_at = datetime.now(timezone.utc)
    all_passed = all(case.passed for case in results)

    run_id = uuid4()
    test_run = TestRun(
        run_id=run_id,
        build_id=payload.build_id,
        status="passed" if all_passed else "failed",
        started_at=started_at,
        completed_at=completed_at,
        results=results,
    )
    TEST_RUNS[str(run_id)] = test_run
    return test_run


def get_test_run(run_id: UUID) -> TestRun | None:
    return TEST_RUNS.get(str(run_id))
