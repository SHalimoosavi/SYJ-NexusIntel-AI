import pytest
from fastapi import HTTPException, Response
from fastapi.testclient import TestClient
from starlette.requests import Request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.dependencies import get_current_user
from app.core.rate_limit import RateLimitBackendUnavailable, RateLimitManager
from app.core.security import create_access_token, create_refresh_token, hash_password, verify_password
from app.database.database import Base, get_db
from app.main import app
from app.models.organization import Organization
from app.models.role import Role
from app.models.user import User
import app.routers.auth as auth_router


@pytest.fixture
def auth_session(monkeypatch):
    monkeypatch.setenv("COOKIE_SECURE", "false")
    monkeypatch.setenv("COOKIE_SAMESITE", "lax")
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:3000")

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    db = sessionmaker(bind=engine)()
    org = Organization(name="Session Tenant", slug="session-tenant")
    role = Role(name="ORGANIZATION_OWNER")
    db.add_all([org, role])
    db.commit()
    db.refresh(org)
    db.refresh(role)
    user = User(
        full_name="Session User",
        email="session-user@example.com",
        hashed_password=hash_password("OldPassword123!"),
        organization_id=org.id,
        role_id=role.id,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    def override_db():
        yield db

    app.dependency_overrides[get_db] = override_db
    yield db, user
    app.dependency_overrides.clear()
    db.close()
    Base.metadata.drop_all(bind=engine)


def test_logout_revokes_access_and_refresh_session_family(monkeypatch, auth_session):
    _db, user = auth_session
    manager = RateLimitManager(redis_url="", app_env="test")
    monkeypatch.setattr(auth_router, "rate_limit_manager", manager)
    token = create_access_token(
        {"sub": user.email, "user_id": user.id, "session_version": 0}
    )
    client = TestClient(app)
    client.cookies.set("access_token", token)
    response = client.post(
        "/auth/logout",
        headers={"Origin": "http://localhost:3000"},
    )
    assert response.status_code == 200
    assert manager.get_user_session_version(user.id) == 1


def test_refresh_rotation_rejects_reuse_and_revokes_session_family(monkeypatch, auth_session):
    db, user = auth_session
    manager = RateLimitManager(redis_url="", app_env="test")
    monkeypatch.setattr(auth_router, "rate_limit_manager", manager)
    old_refresh = create_refresh_token(
        {"sub": user.email, "user_id": user.id, "session_version": 0}
    )

    def refresh_request():
        return Request({
            "type": "http",
            "method": "POST",
            "scheme": "http",
            "path": "/auth/refresh",
            "query_string": b"",
            "headers": [
                (b"origin", b"http://localhost:3000"),
                (b"cookie", f"refresh_token={old_refresh}".encode("ascii")),
            ],
            "client": ("127.0.0.1", 12345),
            "server": ("testserver", 80),
        })

    first_response = Response()
    first = auth_router.refresh_session(refresh_request(), first_response, db)
    assert first == {"success": True, "token_type": "cookie"}
    assert any(
        key == b"set-cookie" and b"refresh_token=" in value
        for key, value in first_response.raw_headers
    )

    concurrent_response = Response()
    concurrent = auth_router.refresh_session(refresh_request(), concurrent_response, db)
    assert concurrent == {"success": True, "token_type": "cookie"}
    first_refresh_cookie = next(
        value for key, value in first_response.raw_headers
        if key == b"set-cookie" and b"refresh_token=" in value
    )
    concurrent_refresh_cookie = next(
        value for key, value in concurrent_response.raw_headers
        if key == b"set-cookie" and b"refresh_token=" in value
    )
    assert first_refresh_cookie == concurrent_refresh_cookie
    assert manager.get_user_session_version(user.id) == 0

    # Once the short idempotency grace has expired, the same token is theft/replay.
    manager._memory_refresh_results.clear()
    manager._memory_refresh_inflight.clear()
    with pytest.raises(HTTPException) as replay:
        auth_router.refresh_session(refresh_request(), Response(), db)
    assert replay.value.status_code == 401
    assert manager.get_user_session_version(user.id) == 1


def test_password_change_rotates_password_and_revokes_old_sessions(monkeypatch, auth_session):
    db, user = auth_session
    manager = RateLimitManager(redis_url="", app_env="test")
    monkeypatch.setattr(auth_router, "rate_limit_manager", manager)
    monkeypatch.setattr(
        "app.core.dependencies.rate_limit_manager",
        manager,
    )
    app.dependency_overrides[get_current_user] = lambda: {
        "user_id": user.id,
        "sub": user.email,
        "organization_id": user.organization_id,
        "role_id": user.role_id,
        "role_name": "ORGANIZATION_OWNER",
    }
    client = TestClient(app)
    response = client.post(
        "/auth/change-password",
        json={
            "current_password": "OldPassword123!",
            "new_password": "NewPassword123!Secure",
        },
    )
    assert response.status_code == 200
    db.refresh(user)
    assert verify_password("NewPassword123!Secure", user.hashed_password)
    assert not verify_password("OldPassword123!", user.hashed_password)
    assert manager.get_user_session_version(user.id) == 1



def test_bruteforce_lockout_and_unknown_user_share_generic_error(monkeypatch, auth_session):
    _db, user = auth_session
    manager = RateLimitManager(redis_url="", app_env="test")
    monkeypatch.setattr(auth_router, "rate_limit_manager", manager)
    monkeypatch.setattr(auth_router.time, "sleep", lambda _seconds: None)
    client = TestClient(app)
    headers = {"Origin": "http://localhost:3000"}

    wrong_password = client.post(
        "/auth/login",
        json={"email": user.email, "password": "WrongPassword123!"},
        headers=headers,
    )
    unknown_user = client.post(
        "/auth/login",
        json={"email": "unknown-user@example.com", "password": "WrongPassword123!"},
        headers=headers,
    )
    assert wrong_password.status_code == 401
    assert unknown_user.status_code == 401
    assert wrong_password.json() == unknown_user.json() == {"detail": "Invalid credentials"}

    for _ in range(4):
        blocked_attempt = client.post(
            "/auth/login",
            json={"email": user.email, "password": "WrongPassword123!"},
            headers=headers,
        )
        assert blocked_attempt.status_code == 401
        assert blocked_attempt.json() == {"detail": "Invalid credentials"}

    locked_attempt = client.post(
        "/auth/login",
        json={"email": user.email, "password": "WrongPassword123!"},
        headers=headers,
    )
    assert locked_attempt.status_code == 401
    assert locked_attempt.json() == {"detail": "Invalid credentials"}

def test_logout_during_refresh_invalidates_the_pending_refresh_token(monkeypatch, auth_session):
    db, user = auth_session
    manager = RateLimitManager(redis_url="", app_env="test")
    monkeypatch.setattr(auth_router, "rate_limit_manager", manager)
    refresh_token = create_refresh_token(
        {"sub": user.email, "user_id": user.id, "session_version": 0}
    )
    access_token = create_access_token(
        {"sub": user.email, "user_id": user.id, "session_version": 0}
    )
    logout_request = Request({
        "type": "http",
        "method": "POST",
        "scheme": "http",
        "path": "/auth/logout",
        "query_string": b"",
        "headers": [
            (b"origin", b"http://localhost:3000"),
            (b"cookie", f"access_token={access_token}".encode("ascii")),
        ],
        "client": ("127.0.0.1", 12345),
        "server": ("testserver", 80),
    })
    auth_router.logout(logout_request, Response(), db)

    refresh_request = Request({
        "type": "http",
        "method": "POST",
        "scheme": "http",
        "path": "/auth/refresh",
        "query_string": b"",
        "headers": [
            (b"origin", b"http://localhost:3000"),
            (b"cookie", f"refresh_token={refresh_token}".encode("ascii")),
        ],
        "client": ("127.0.0.1", 12345),
        "server": ("testserver", 80),
    })
    with pytest.raises(HTTPException) as expired:
        auth_router.refresh_session(refresh_request, Response(), db)
    assert expired.value.status_code == 401


def test_refresh_fails_closed_when_session_backend_is_unavailable(monkeypatch, auth_session):
    db, user = auth_session
    token = create_refresh_token(
        {"sub": user.email, "user_id": user.id, "session_version": 0}
    )

    class UnavailableManager:
        def get_user_session_version(self, _user_id):
            return 0

        def begin_refresh_rotation(self, *_args):
            raise RateLimitBackendUnavailable("test outage")

    monkeypatch.setattr(auth_router, "rate_limit_manager", UnavailableManager())
    request = Request({
        "type": "http",
        "method": "POST",
        "scheme": "http",
        "path": "/auth/refresh",
        "query_string": b"",
        "headers": [
            (b"origin", b"http://localhost:3000"),
            (b"cookie", f"refresh_token={token}".encode("ascii")),
        ],
        "client": ("127.0.0.1", 12345),
        "server": ("testserver", 80),
    })
    with pytest.raises(HTTPException) as unavailable:
        auth_router.refresh_session(request, Response(), db)
    assert unavailable.value.status_code == 503


def test_refresh_missing_cached_result_fails_closed(monkeypatch, auth_session):
    db, user = auth_session
    token = create_refresh_token(
        {"sub": user.email, "user_id": user.id, "session_version": 0}
    )

    class MissingResultManager:
        def get_user_session_version(self, _user_id):
            return 0

        def begin_refresh_rotation(self, *_args):
            return 2

        def get_refresh_rotation_result(self, _jti):
            return None

    monkeypatch.setattr(auth_router, "rate_limit_manager", MissingResultManager())
    monkeypatch.setattr(auth_router.time, "sleep", lambda _seconds: None)
    request = Request({
        "type": "http",
        "method": "POST",
        "scheme": "http",
        "path": "/auth/refresh",
        "query_string": b"",
        "headers": [
            (b"origin", b"http://localhost:3000"),
            (b"cookie", f"refresh_token={token}".encode("ascii")),
        ],
        "client": ("127.0.0.1", 12345),
        "server": ("testserver", 80),
    })
    with pytest.raises(HTTPException) as unavailable:
        auth_router.refresh_session(request, Response(), db)
    assert unavailable.value.status_code == 503
    assert unavailable.value.detail == "Session refresh is still processing; retry shortly"
