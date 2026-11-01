import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.dependencies import get_current_user
from app.core.rate_limit import RateLimitManager
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
    _db, user = auth_session
    manager = RateLimitManager(redis_url="", app_env="test")
    monkeypatch.setattr(auth_router, "rate_limit_manager", manager)
    old_refresh = create_refresh_token(
        {"sub": user.email, "user_id": user.id, "session_version": 0}
    )
    client = TestClient(app)
    client.cookies.set("refresh_token", old_refresh)

    first = client.post(
        "/auth/refresh",
        headers={"Origin": "http://localhost:3000"},
    )
    assert first.status_code == 200

    client.cookies.set("refresh_token", old_refresh)
    replay = client.post(
        "/auth/refresh",
        headers={"Origin": "http://localhost:3000"},
    )
    assert replay.status_code == 401
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
