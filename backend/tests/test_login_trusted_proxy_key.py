from fastapi import HTTPException, Response
from starlette.requests import Request

from app.schemas.user import UserLogin
import app.routers.auth as auth_router


def test_login_rate_limit_key_uses_resolved_trusted_proxy_client_ip(monkeypatch):
    monkeypatch.setenv("TRUSTED_PROXIES", "172.30.0.0/24")
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:3000")
    monkeypatch.setattr(auth_router, "authenticate_user", lambda *_args: None)
    monkeypatch.setattr(auth_router.time, "sleep", lambda _seconds: None)

    class RecordingManager:
        def __init__(self):
            self.failure_keys = []

        def is_login_locked(self, _key):
            return False

        def record_login_failure(self, key, **_kwargs):
            self.failure_keys.append(key)
            return 1

        def clear_login_failures(self, _key):
            return None

    manager = RecordingManager()
    monkeypatch.setattr(auth_router, "rate_limit_manager", manager)
    request = Request({
        "type": "http",
        "method": "POST",
        "scheme": "http",
        "path": "/auth/login",
        "query_string": b"",
        "headers": [
            (b"origin", b"http://localhost:3000"),
            (b"x-forwarded-for", b"198.51.100.25, 172.30.0.3"),
        ],
        "client": ("172.30.0.2", 12345),
        "server": ("testserver", 80),
    })

    try:
        auth_router.login(
            UserLogin(email="user@example.com", password="WrongPassword123!"),
            request,
            Response(),
            None,
        )
    except HTTPException as error:
        assert error.status_code == 401
    else:
        raise AssertionError("invalid credentials must be rejected")

    assert manager.failure_keys[0] == auth_router._login_attempt_key(
        "198.51.100.25",
        "user@example.com",
    )
    assert "172.30.0.2" not in manager.failure_keys[0]
