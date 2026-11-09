from datetime import datetime, timezone
from uuid import UUID, uuid4

from app.clients.router_client import get_health
from app.data.builds import BUILDS
from app.data.test_runs import TEST_RUNS
from app.schemas.test_run import TestCaseResult, TestRun, TestRunCreate


def _health_failure_reason(health: dict) -> str | None:
    # Client set error when request never completed (timeout, connection refused, etc.)
    if health["error"] is not None:
        return health["error"]
    if health["status_code"] != 200:
        return f"expected status 200, got {health['status_code']}"
    body = health.get("body")
    if body is None or body.get("status") != "OK":
        return f"unexpected body: {body!r}"
    return None


def create_test_run(payload: TestRunCreate) -> TestRun | None:
    # Cannot test a release we never registered
    if str(payload.build_id) not in BUILDS:
        return None

    started_at = datetime.now(timezone.utc)
    # httpx call only — no pass/fail logic in router_client
    health = get_health()
    completed_at = datetime.now(timezone.utc)

    # Match fake-router normal mode: 200 and {"status": "OK"}
    passed = (
        health["error"] is None
        and health["status_code"] == 200
        and health["body"] is not None
        and health["body"].get("status") == "OK"
    )

    test_case = TestCaseResult(
        test_name="health_check",
        endpoint="/health",
        status_code=health["status_code"],
        latency_ms=health["latency_ms"],
        passed=passed,
        failure_reason=None if passed else _health_failure_reason(health),
    )

    run_id = uuid4()
    # TestRun wraps the case list; run status mirrors the single case for now
    test_run = TestRun(
        run_id=run_id,
        build_id=payload.build_id,
        status="passed" if passed else "failed",
        started_at=started_at,
        completed_at=completed_at,
        results=[test_case],
    )
    TEST_RUNS[str(run_id)] = test_run
    return test_run


def get_test_run(run_id: UUID) -> TestRun | None:
    return TEST_RUNS.get(str(run_id))
