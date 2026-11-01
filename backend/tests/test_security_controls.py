from pathlib import Path

from fastapi.testclient import TestClient

from app.core.rate_limit import RateLimitManager
from app.main import app
import app.main as main_module


def test_global_rate_limit_returns_429_and_retry_after(monkeypatch):
    manager = RateLimitManager(redis_url="", app_env="test")
    monkeypatch.setattr(main_module, "rate_limit_manager", manager)
    monkeypatch.setattr(main_module, "rate_limit_policy_for_path", lambda _path: (1, 60))
    client = TestClient(app)
    assert client.get("/health").status_code == 200
    response = client.get("/health")
    assert response.status_code == 429
    assert int(response.headers["Retry-After"]) >= 1


def test_untrusted_forwarded_for_header_does_not_set_client_ip(monkeypatch):
    observed = []

    class RecordingLimiter:
        def check(self, key, _limit, _window):
            observed.append(key)
            return True, 0

    monkeypatch.setattr(main_module, "rate_limit_manager", RecordingLimiter())
    client = TestClient(app)
    response = client.get("/health", headers={"X-Forwarded-For": "203.0.113.99"})
    assert response.status_code == 200
    assert observed
    assert "203.0.113.99" not in observed[0]
    assert "testclient" in observed[0]


def test_self_hosted_proxy_configuration_has_network_limits():
    root = Path(__file__).resolve().parents[2]
    nginx = (root / "deploy" / "nginx" / "nginx.conf.template").read_text()
    compose = (root / "docker-compose.yml").read_text()
    assert "limit_req_zone" in nginx
    assert "limit_conn_zone" in nginx
    assert "client_max_body_size 10m" in nginx
    assert "client_header_timeout" in nginx
    assert "gzip on" in nginx
    backend_block = compose.split("  backend:", 1)[1].split("  frontend:", 1)[0]
    assert "ports:" not in backend_block
