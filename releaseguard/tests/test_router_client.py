import os
from unittest.mock import patch

from app.clients import router_client


def test_get_base_url_defaults_to_localhost():
    env = {k: v for k, v in os.environ.items() if k != router_client.FAKE_ROUTER_URL_ENV}
    with patch.dict(os.environ, env, clear=True):
        assert router_client.get_base_url() == router_client.DEFAULT_BASE_URL


def test_get_base_url_reads_fake_router_url_env():
    with patch.dict(os.environ, {router_client.FAKE_ROUTER_URL_ENV: "http://router:9001/"}):
        assert router_client.get_base_url() == "http://router:9001"


def test_set_fault_mode_posts_admin_payload():
    fake = {
        "status_code": 200,
        "latency_ms": 1.0,
        "body": {
            "mode": "slow",
            "delay_ms": 2000,
            "error_rate": 0.3,
            "message": "Fault mode set to slow",
        },
        "error": None,
    }
    with patch.object(router_client, "_request", return_value=fake) as mock_request:
        result = router_client.set_fault_mode("slow", delay_ms=2000, error_rate=0.3)

    assert result == fake
    mock_request.assert_called_once_with(
        "POST",
        "/admin/fault-mode",
        json={"mode": "slow", "delay_ms": 2000, "error_rate": 0.3},
        base_url=None,
        timeout_s=router_client.DEFAULT_TIMEOUT_S,
    )


def test_reset_fault_mode_sets_normal():
    fake = {
        "status_code": 200,
        "latency_ms": 1.0,
        "body": {
            "mode": "normal",
            "delay_ms": 2000,
            "error_rate": 0.3,
            "message": "Fault mode set to normal",
        },
        "error": None,
    }
    with patch.object(router_client, "set_fault_mode", return_value=fake) as mock_set:
        result = router_client.reset_fault_mode()

    assert result == fake
    mock_set.assert_called_once_with(
        "normal",
        delay_ms=2000,
        error_rate=0.3,
        base_url=None,
        timeout_s=router_client.DEFAULT_TIMEOUT_S,
    )


def test_request_uses_env_base_url_when_not_overridden():
    class FakeResponse:
        status_code = 200

        def json(self):
            return {"status": "OK"}

    with patch.dict(os.environ, {router_client.FAKE_ROUTER_URL_ENV: "http://fake-router:8001"}):
        with patch(
            "app.clients.router_client.httpx.request",
            return_value=FakeResponse(),
        ) as mock_httpx:
            result = router_client.get_health()

    assert result["status_code"] == 200
    assert result["body"] == {"status": "OK"}
    mock_httpx.assert_called_once()
    assert mock_httpx.call_args.args[0] == "GET"
    assert mock_httpx.call_args.args[1] == "http://fake-router:8001/health"
