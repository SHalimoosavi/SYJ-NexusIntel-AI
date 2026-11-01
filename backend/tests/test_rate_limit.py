from app.core.rate_limit import SlidingWindowLimiter


def test_sliding_window_rejects_requests_over_limit(monkeypatch):
    import app.core.rate_limit as module

    now = [100.0]
    monkeypatch.setattr(module, "monotonic", lambda: now[0])
    limiter = SlidingWindowLimiter()
    assert limiter.allow("client", 2, 60)
    assert limiter.allow("client", 2, 60)
    assert not limiter.allow("client", 2, 60)
    now[0] = 161.0
    assert limiter.allow("client", 2, 60)
