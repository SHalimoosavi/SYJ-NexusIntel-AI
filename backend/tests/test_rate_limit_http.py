from fastapi.testclient import TestClient

from app.core.rate_limit import RateLimitManager
from app import main


def test_rate_limit_returns_429_with_retry_after(monkeypatch):
    manager = RateLimitManager(redis_url="", app_env="test")
    monkeypatch.setattr(main, "rate_limit_manager", manager)
    monkeypatch.setattr(main, "rate_limit_policy_for_path", lambda _path: (1, 60))

    with TestClient(main.app) as client:
        first = client.get("/health")
        second = client.get("/health")

    assert first.status_code == 200
    assert second.status_code == 429
    assert int(second.headers["Retry-After"]) >= 1
