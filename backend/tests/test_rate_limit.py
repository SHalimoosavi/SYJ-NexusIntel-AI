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
        ("/auth/login", (10, 900)),
        ("/auth/register", (3, 3600)),
        ("/auth/password-reset", (3, 3600)),
        ("/auth/refresh", (10, 60)),
        ("/auth/logout", (20, 60)),
        ("/auth/unimplemented-route", (20, 60)),
        ("/invitations/accept", (5, 3600)),
        ("/leads", (120, 60)),
    ],
)
def test_route_policy(path, expected):
    assert rate_limit_policy_for_path(path) == expected


def test_login_failures_trigger_temporary_lockout_and_clear():
    manager = RateLimitManager(redis_url=None, app_env="test")
    key = "login-attempt:hashed"
    account_key = "account-login-attempt:hashed"
    assert not manager.is_login_locked(key)
    for _ in range(4):
        assert manager.record_login_failure(key, threshold=5) < 5
        manager.record_login_failure(account_key, threshold=10)
    assert manager.record_login_failure(key, threshold=5) == 5
    assert manager.record_login_failure(account_key, threshold=10) == 5
    assert manager.is_login_locked(key)
    assert not manager.is_login_locked(account_key)
    for _ in range(5):
        manager.record_login_failure(account_key, threshold=10)
    assert manager.is_login_locked(account_key)
    manager.clear_login_failures(key)
    manager.clear_login_failures(account_key)
    assert not manager.is_login_locked(key)
    assert not manager.is_login_locked(account_key)


def test_user_and_organization_quotas_use_independent_buckets():
    manager = RateLimitManager(redis_url=None, app_env="test")
    assert manager.check("user:101", 1, 60) == (True, 0)
    assert manager.check("user:101", 1, 60)[0] is False
    # A different user and the shared organization bucket have independent keys.
    assert manager.check("user:202", 1, 60) == (True, 0)
    assert manager.check("organization:55", 1, 60) == (True, 0)
    assert manager.check("organization:55", 1, 60)[0] is False


def test_retry_after_is_returned_when_bucket_is_full():
    manager = RateLimitManager(redis_url=None, app_env="test")
    assert manager.check("limited", 1, 60) == (True, 0)
    allowed, retry_after = manager.check("limited", 1, 60)
    assert not allowed
    assert 1 <= retry_after <= 60
