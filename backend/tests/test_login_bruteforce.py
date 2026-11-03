from fastapi import HTTPException, Response

from app.core.rate_limit import RateLimitManager
from app.routers import auth
from app.schemas.user import UserLogin
from starlette.requests import Request


def _request(ip: str) -> Request:
    return Request({
        "type": "http",
        "method": "POST",
        "scheme": "http",
        "path": "/auth/login",
        "query_string": b"",
        "headers": [(b"origin", b"http://localhost:3000")],
        "client": (ip, 12345),
        "server": ("testserver", 80),
    })


def _attempt(ip: str, email: str):
    credentials = UserLogin(email=email, password="wrong-password-123")
    try:
        auth.login(credentials, _request(ip), Response(), db=None)
    except HTTPException as error:
        return error.status_code, error.detail
    raise AssertionError("Invalid credentials must be rejected")


def test_bruteforce_lockout_returns_same_generic_error(monkeypatch):
    manager = RateLimitManager(redis_url="", app_env="test")
    monkeypatch.setattr(auth, "rate_limit_manager", manager)
    monkeypatch.setattr(auth, "authenticate_user", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(auth.time, "sleep", lambda *_args, **_kwargs: None)

    responses = [
        _attempt("198.51.100.10", "victim@example.com")
        for _ in range(6)
    ]
    assert responses == [(401, "Invalid credentials")] * 6


def test_account_lockout_applies_across_multiple_source_ips(monkeypatch):
    manager = RateLimitManager(redis_url="", app_env="test")
    monkeypatch.setattr(auth, "rate_limit_manager", manager)
    monkeypatch.setattr(auth, "authenticate_user", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(auth.time, "sleep", lambda *_args, **_kwargs: None)

    for index in range(10):
        ip = f"198.51.100.{index + 10}"
        assert _attempt(ip, "victim@example.com") == (401, "Invalid credentials")

    assert _attempt("203.0.113.99", "victim@example.com") == (
        401,
        "Invalid credentials",
    )
