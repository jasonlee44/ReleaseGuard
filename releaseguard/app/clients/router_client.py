import time

import httpx

DEFAULT_BASE_URL = "http://localhost:8001"
DEFAULT_TIMEOUT_S = 5.0


def _get(path: str, base_url: str = DEFAULT_BASE_URL, timeout_s: float = DEFAULT_TIMEOUT_S) -> dict:
    started = time.perf_counter()
    url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"
    try:
        response = httpx.get(url, timeout=timeout_s)
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


def get_health(base_url: str = DEFAULT_BASE_URL, timeout_s: float = DEFAULT_TIMEOUT_S) -> dict:
    return _get("/health", base_url=base_url, timeout_s=timeout_s)


def get_devices(base_url: str = DEFAULT_BASE_URL, timeout_s: float = DEFAULT_TIMEOUT_S) -> dict:
    return _get("/devices", base_url=base_url, timeout_s=timeout_s)


def get_device_status(
    device_id: str,
    base_url: str = DEFAULT_BASE_URL,
    timeout_s: float = DEFAULT_TIMEOUT_S,
) -> dict:
    return _get(f"/devices/{device_id}/status", base_url=base_url, timeout_s=timeout_s)


def get_device_config(
    device_id: str,
    base_url: str = DEFAULT_BASE_URL,
    timeout_s: float = DEFAULT_TIMEOUT_S,
) -> dict:
    return _get(f"/devices/{device_id}/config", base_url=base_url, timeout_s=timeout_s)


def get_firmware_version(
    base_url: str = DEFAULT_BASE_URL,
    timeout_s: float = DEFAULT_TIMEOUT_S,
) -> dict:
    return _get("/firmware/version", base_url=base_url, timeout_s=timeout_s)
