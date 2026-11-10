from datetime import datetime, timezone
from uuid import UUID, uuid4

from app.clients import router_client
from app.data.builds import BUILDS
from app.data.test_runs import TEST_RUNS
from app.schemas.test_run import TestCaseResult, TestRun, TestRunCreate

# Seeded device used for status/config checks against fake-router
PROBE_DEVICE_ID = "router-001"
# Config payload used by the config_update probe (POST /devices/{id}/config)
PROBE_CONFIG = {
    "hostname": "rg-probe-01",
    "vlan_ids": [10, 20, 99],
    "routing_enabled": True,
}
# Distinct payload for config_bug persistence check
REGRESSION_CONFIG = {
    "hostname": "rg-regression",
    "vlan_ids": [42],
    "routing_enabled": False,
}

# Reliability probe knobs (used by slow / error_prone / down / config_bug cases)
LATENCY_THRESHOLD_MS = 500.0
SLOW_DELAY_MS = 2000
ERROR_PRONE_RATE = 1.0


def _ensure_fault_mode(
    mode: str,
    *,
    delay_ms: int = SLOW_DELAY_MS,
    error_rate: float = ERROR_PRONE_RATE,
) -> dict:
    """Set fake-router fault mode; return the admin API response dict."""
    return router_client.set_fault_mode(mode, delay_ms=delay_ms, error_rate=error_rate)


def _reset_fault_mode() -> dict:
    """Best-effort restore to normal so later cases are not contaminated."""
    return router_client.reset_fault_mode()


def _transport_failure_reason(response: dict) -> str | None:
    if response["error"] is not None:
        return response["error"]
    if response["status_code"] != 200:
        return f"expected status 200, got {response['status_code']}"
    if response.get("body") is None:
        return "expected JSON body, got none"
    return None


def _actual_from_response(response: dict) -> str:
    if response["error"] is not None:
        return f"error={response['error']!r} latency_ms={response['latency_ms']:.1f}"
    return (
        f"status_code={response['status_code']}, "
        f"latency_ms={response['latency_ms']:.1f}, "
        f"body={response['body']!r}"
    )


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


def _evaluate_config_update(
    response: dict,
    device_id: str,
    expected_config: dict,
) -> tuple[bool, str | None]:
    reason = _transport_failure_reason(response)
    if reason is not None:
        return False, reason
    body = response["body"]
    if body.get("device_id") != device_id:
        return False, f"unexpected device_id: {body!r}"
    if not isinstance(body.get("config_version"), int):
        return False, f"missing config_version: {body!r}"
    returned = body.get("config")
    if not isinstance(returned, dict):
        return False, f"unexpected config: {returned!r}"
    for key, value in expected_config.items():
        if returned.get(key) != value:
            return False, f"config field {key!r} expected {value!r}, got {returned.get(key)!r}"
    return True, None


def _evaluate_firmware(response: dict) -> tuple[bool, str | None]:
    reason = _transport_failure_reason(response)
    if reason is not None:
        return False, reason
    body = response["body"]
    if not body.get("product") or not body.get("firmware_version"):
        return False, f"unexpected body: {body!r}"
    return True, None


def _evaluate_slow_latency(response: dict) -> tuple[bool, str | None]:
    """Release fails if the endpoint is too slow under injected delay (option A)."""
    reason = _transport_failure_reason(response)
    if reason is not None:
        return False, reason
    latency = response["latency_ms"]
    if latency > LATENCY_THRESHOLD_MS:
        return (
            False,
            f"latency {latency:.1f}ms exceeded threshold {LATENCY_THRESHOLD_MS:.0f}ms",
        )
    return True, None


def _evaluate_config_regression(
    get_response: dict,
    device_id: str,
    expected_config: dict,
) -> tuple[bool, str | None]:
    """Release fails if written config did not persist (config_bug behavior)."""
    reason = _transport_failure_reason(get_response)
    if reason is not None:
        return False, reason
    body = get_response["body"]
    if body.get("device_id") != device_id:
        return False, f"unexpected device_id: {body!r}"
    returned = body.get("config")
    if not isinstance(returned, dict):
        return False, f"unexpected config: {returned!r}"
    for key, value in expected_config.items():
        if returned.get(key) != value:
            return (
                False,
                f"config did not persist: field {key!r} expected {value!r}, "
                f"got {returned.get(key)!r}",
            )
    return True, None


def _run_case(
    test_name: str,
    endpoint: str,
    response: dict,
    passed: bool,
    failure_reason: str | None,
    expected_result: str,
    actual_result: str | None = None,
) -> TestCaseResult:
    return TestCaseResult(
        test_name=test_name,
        endpoint=endpoint,
        expected_result=expected_result,
        actual_result=actual_result if actual_result is not None else _actual_from_response(response),
        status_code=response["status_code"],
        latency_ms=response["latency_ms"],
        passed=passed,
        failure_reason=failure_reason,
    )


def _build_summary(results: list[TestCaseResult]) -> str:
    total = len(results)
    passed_count = sum(1 for case in results if case.passed)
    failed = [case.test_name for case in results if not case.passed]
    if not failed:
        return f"{passed_count}/{total} passed"
    return f"{passed_count}/{total} passed; failed: {', '.join(failed)}"


def _run_health_check_case() -> TestCaseResult:
    response = router_client.get_health()
    passed, reason = _evaluate_health(response)
    return _run_case(
        "health_check",
        "/health",
        response,
        passed,
        reason,
        expected_result="HTTP 200 with body status=OK",
    )


def _run_devices_list_case() -> TestCaseResult:
    response = router_client.get_devices()
    passed, reason = _evaluate_devices_list(response)
    return _run_case(
        "devices_list",
        "/devices",
        response,
        passed,
        reason,
        expected_result="HTTP 200 with non-empty devices list matching count",
    )


def _run_device_status_case() -> TestCaseResult:
    response = router_client.get_device_status(PROBE_DEVICE_ID)
    passed, reason = _evaluate_device_status(response, PROBE_DEVICE_ID)
    return _run_case(
        "device_status",
        f"/devices/{PROBE_DEVICE_ID}/status",
        response,
        passed,
        reason,
        expected_result=f"HTTP 200 with device_id={PROBE_DEVICE_ID} and online field",
    )


def _run_device_config_case() -> TestCaseResult:
    response = router_client.get_device_config(PROBE_DEVICE_ID)
    passed, reason = _evaluate_device_config(response, PROBE_DEVICE_ID)
    return _run_case(
        "device_config",
        f"/devices/{PROBE_DEVICE_ID}/config",
        response,
        passed,
        reason,
        expected_result=f"HTTP 200 with device_id={PROBE_DEVICE_ID} and config hostname/vlan_ids",
    )


def _run_config_update_case() -> TestCaseResult:
    response = router_client.update_device_config(PROBE_DEVICE_ID, PROBE_CONFIG)
    passed, reason = _evaluate_config_update(response, PROBE_DEVICE_ID, PROBE_CONFIG)
    return _run_case(
        "config_update",
        f"/devices/{PROBE_DEVICE_ID}/config",
        response,
        passed,
        reason,
        expected_result=(
            f"HTTP 200 POST echoing device_id={PROBE_DEVICE_ID} "
            f"and config={PROBE_CONFIG!r}"
        ),
    )


def _run_firmware_version_case() -> TestCaseResult:
    response = router_client.get_firmware_version()
    passed, reason = _evaluate_firmware(response)
    return _run_case(
        "firmware_version",
        "/firmware/version",
        response,
        passed,
        reason,
        expected_result="HTTP 200 with product and firmware_version",
    )


def _run_slow_response_case() -> TestCaseResult:
    endpoint = f"/devices/{PROBE_DEVICE_ID}/status"
    expected = (
        f"HTTP 200 with latency_ms <= {LATENCY_THRESHOLD_MS:.0f} "
        f"under fault mode slow (delay_ms={SLOW_DELAY_MS})"
    )
    try:
        _ensure_fault_mode("slow", delay_ms=SLOW_DELAY_MS)
        response = router_client.get_device_status(PROBE_DEVICE_ID)
        passed, reason = _evaluate_slow_latency(response)
        return _run_case(
            "slow_response",
            endpoint,
            response,
            passed,
            reason,
            expected_result=expected,
        )
    finally:
        _reset_fault_mode()


def _run_error_prone_case() -> TestCaseResult:
    endpoint = "/health"
    expected = f"HTTP 200 with status=OK under fault mode error_prone (error_rate={ERROR_PRONE_RATE})"
    try:
        _ensure_fault_mode("error_prone", error_rate=ERROR_PRONE_RATE)
        response = router_client.get_health()
        passed, reason = _evaluate_health(response)
        return _run_case(
            "error_prone_service",
            endpoint,
            response,
            passed,
            reason,
            expected_result=expected,
        )
    finally:
        _reset_fault_mode()


def _run_down_service_case() -> TestCaseResult:
    endpoint = "/health"
    expected = "HTTP 200 with status=OK under fault mode down"
    try:
        _ensure_fault_mode("down")
        response = router_client.get_health()
        passed, reason = _evaluate_health(response)
        return _run_case(
            "down_service",
            endpoint,
            response,
            passed,
            reason,
            expected_result=expected,
        )
    finally:
        _reset_fault_mode()


def _run_config_regression_case() -> TestCaseResult:
    endpoint = f"/devices/{PROBE_DEVICE_ID}/config"
    expected = (
        f"POST then GET persists config={REGRESSION_CONFIG!r} "
        f"for device_id={PROBE_DEVICE_ID} under fault mode config_bug"
    )
    try:
        _ensure_fault_mode("config_bug")
        post_response = router_client.update_device_config(
            PROBE_DEVICE_ID, REGRESSION_CONFIG
        )
        get_response = router_client.get_device_config(PROBE_DEVICE_ID)
        # Persistence is judged by the GET; POST may lie under config_bug
        passed, reason = _evaluate_config_regression(
            get_response, PROBE_DEVICE_ID, REGRESSION_CONFIG
        )
        actual = (
            f"POST {_actual_from_response(post_response)}; "
            f"GET {_actual_from_response(get_response)}"
        )
        return _run_case(
            "config_regression",
            endpoint,
            get_response,
            passed,
            reason,
            expected_result=expected,
            actual_result=actual,
        )
    finally:
        _reset_fault_mode()


# Ship-gate happy path (cases 1–6) vs intentional reliability probes (cases 7–10)
DEFAULT_CASE_RUNNERS = (
    _run_health_check_case,
    _run_devices_list_case,
    _run_device_status_case,
    _run_device_config_case,
    _run_config_update_case,
    _run_firmware_version_case,
)

CHAOS_CASE_RUNNERS = (
    _run_slow_response_case,
    _run_error_prone_case,
    _run_down_service_case,
    _run_config_regression_case,
)

ALL_CASE_RUNNERS = DEFAULT_CASE_RUNNERS + CHAOS_CASE_RUNNERS


def create_test_run(payload: TestRunCreate) -> TestRun | None:
    # Cannot test a release we never registered
    if str(payload.build_id) not in BUILDS:
        return None

    runners = (
        DEFAULT_CASE_RUNNERS
        if payload.suite == "default"
        else CHAOS_CASE_RUNNERS
    )

    started_at = datetime.now(timezone.utc)
    results: list[TestCaseResult] = []

    try:
        # Start from a known-good fault mode, then run the selected suite
        _reset_fault_mode()
        for run_case in runners:
            results.append(run_case())
    finally:
        # Belt-and-suspenders: never leave fake-router stuck in a fault mode
        _reset_fault_mode()

    completed_at = datetime.now(timezone.utc)
    all_passed = all(case.passed for case in results)
    summary = _build_summary(results)

    run_id = uuid4()
    test_run = TestRun(
        run_id=run_id,
        build_id=payload.build_id,
        suite=payload.suite,
        status="passed" if all_passed else "failed",
        summary=summary,
        started_at=started_at,
        completed_at=completed_at,
        results=results,
    )
    TEST_RUNS[str(run_id)] = test_run
    return test_run


def list_test_runs() -> list[TestRun]:
    return list(TEST_RUNS.values())


def get_test_run(run_id: UUID) -> TestRun | None:
    return TEST_RUNS.get(str(run_id))
