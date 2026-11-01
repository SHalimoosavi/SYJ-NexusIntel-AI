import pytest

from app.core.rate_limit import (
    RateLimitBackendUnavailable,
    RateLimitManager,
    SlidingWindowLimiter,
    rate_limit_policy_for_path,
)


def test_sliding_window_rejects_requests_over_limit(monkeypatch):
    import app.core.rate_limit as module

    now = [100.0]
    monkeypatch.setattr(module.time, "monotonic", lambda: now[0])
    limiter = SlidingWindowLimiter()
    assert limiter.check("client", 2, 60) == (True, 0)
    assert limiter.check("client", 2, 60) == (True, 0)
    allowed, retry_after = limiter.check("client", 2, 60)
    assert not allowed
    assert 1 <= retry_after <= 60
    now[0] = 161.0
    assert limiter.check("client", 2, 60)[0]


def test_local_mode_uses_in_memory_fallback():
    manager = RateLimitManager(redis_url=None, app_env="development")
    assert manager.check("ip:127.0.0.1", 1, 60) == (True, 0)
    assert not manager.check("ip:127.0.0.1", 1, 60)[0]


def test_production_without_redis_fails_closed():
    manager = RateLimitManager(redis_url=None, app_env="production")
    with pytest.raises(RateLimitBackendUnavailable):
        manager.check("ip:127.0.0.1", 10, 60)


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        ("/auth/login", (5, 900)),
        ("/auth/register", (3, 3600)),
        ("/auth/password-reset", (3, 3600)),
        ("/auth/refresh", (10, 60)),
        ("/auth/logout", (20, 60)),
        ("/invitations/accept", (5, 3600)),
        ("/leads", (120, 60)),
    ],
)
def test_route_policy(path, expected):
    assert rate_limit_policy_for_path(path) == expected


def test_login_failures_trigger_temporary_lockout_and_clear():
    manager = RateLimitManager(redis_url=None, app_env="test")
    key = "login-attempt:hashed"
    assert not manager.is_login_locked(key)
    for _ in range(4):
        assert manager.record_login_failure(key, threshold=5) < 5
    assert manager.record_login_failure(key, threshold=5) == 5
    assert manager.is_login_locked(key)
    manager.clear_login_failures(key)
    assert not manager.is_login_locked(key)
