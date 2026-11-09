import time
import httpx

def get_health(base_url: str = "http://localhost:8001", timeout_s: float = 5.0) -> dict:
    started = time.perf_counter()
    try:
        response = httpx.get(f"{base_url.rstrip('/')}/health", timeout=timeout_s)
    except httpx.TimeoutException:
        latency_ms = (time.perf_counter() - started) * 1000
        return {"status_code": None, "latency_ms": latency_ms, "body": None, "error": "timeout"}
    except httpx.RequestError as exc:
        latency_ms = (time.perf_counter() - started) * 1000
        return {"status_code": None, "latency_ms": latency_ms, "body": None, "error": str(exc)}

    latency_ms = (time.perf_counter() - started) * 1000
    return {
        "status_code": response.status_code,
        "latency_ms": latency_ms,
        "body": response.json(),
        "error": None,
    }
