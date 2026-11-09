import os
import time

import httpx

DEFAULT_BASE_URL = "http://localhost:8001"
DEFAULT_TIMEOUT_S = 5.0
FAKE_ROUTER_URL_ENV = "FAKE_ROUTER_URL"


def get_base_url() -> str:
    """Resolve fake-router base URL from env, falling back to local default."""
    return os.getenv(FAKE_ROUTER_URL_ENV, DEFAULT_BASE_URL).rstrip("/")


def _request(
    method: str,
    path: str,
    *,
    json: dict | None = None,
    base_url: str | None = None,
    timeout_s: float = DEFAULT_TIMEOUT_S,
) -> dict:
    resolved_base = get_base_url() if base_url is None else base_url
    started = time.perf_counter()
    url = f"{resolved_base.rstrip('/')}/{path.lstrip('/')}"
    try:
        response = httpx.request(method, url, json=json, timeout=timeout_s)
    except httpx.TimeoutException:
        latency_ms = (time.perf_counter() - started) * 1000
        return {"status_code": None, "latency_ms": latency_ms, "body": None, "error": "timeout"}
    except httpx.RequestError as exc:
        latency_ms = (time.perf_counter() - started) * 1000
        return {"status_code": None, "latency_ms": latency_ms, "body": None, "error": str(exc)}

    latency_ms = (time.perf_counter() - started) * 1000
    try:
        body = response.json()
    except ValueError:
        body = None
    return {
        "status_code": response.status_code,
        "latency_ms": latency_ms,
        "body": body,
        "error": None,
    }


def _get(path: str, base_url: str | None = None, timeout_s: float = DEFAULT_TIMEOUT_S) -> dict:
    return _request("GET", path, base_url=base_url, timeout_s=timeout_s)


def get_health(base_url: str | None = None, timeout_s: float = DEFAULT_TIMEOUT_S) -> dict:
    return _get("/health", base_url=base_url, timeout_s=timeout_s)


def get_devices(base_url: str | None = None, timeout_s: float = DEFAULT_TIMEOUT_S) -> dict:
    return _get("/devices", base_url=base_url, timeout_s=timeout_s)


def get_device_status(
    device_id: str,
    base_url: str | None = None,
    timeout_s: float = DEFAULT_TIMEOUT_S,
) -> dict:
    return _get(f"/devices/{device_id}/status", base_url=base_url, timeout_s=timeout_s)


def get_device_config(
    device_id: str,
    base_url: str | None = None,
    timeout_s: float = DEFAULT_TIMEOUT_S,
) -> dict:
    return _get(f"/devices/{device_id}/config", base_url=base_url, timeout_s=timeout_s)


def update_device_config(
    device_id: str,
    config: dict,
    base_url: str | None = None,
    timeout_s: float = DEFAULT_TIMEOUT_S,
) -> dict:
    return _request(
        "POST",
        f"/devices/{device_id}/config",
        json={"config": config},
        base_url=base_url,
        timeout_s=timeout_s,
    )


def get_firmware_version(
    base_url: str | None = None,
    timeout_s: float = DEFAULT_TIMEOUT_S,
) -> dict:
    return _get("/firmware/version", base_url=base_url, timeout_s=timeout_s)


def set_fault_mode(
    mode: str,
    *,
    delay_ms: int = 2000,
    error_rate: float = 0.3,
    base_url: str | None = None,
    timeout_s: float = DEFAULT_TIMEOUT_S,
) -> dict:
    """POST /admin/fault-mode on fake-router (not subject to fault injection)."""
    return _request(
        "POST",
        "/admin/fault-mode",
        json={"mode": mode, "delay_ms": delay_ms, "error_rate": error_rate},
        base_url=base_url,
        timeout_s=timeout_s,
    )


def reset_fault_mode(
    base_url: str | None = None,
    timeout_s: float = DEFAULT_TIMEOUT_S,
) -> dict:
    """Return fake-router to normal mode after a reliability probe."""
    return set_fault_mode(
        "normal",
        delay_ms=2000,
        error_rate=0.3,
        base_url=base_url,
        timeout_s=timeout_s,
    )
