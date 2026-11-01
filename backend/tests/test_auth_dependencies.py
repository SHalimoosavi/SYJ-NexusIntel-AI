import json
import os
from types import SimpleNamespace

os.environ.setdefault("JWT_ACTIVE_KID", "test-v1")
os.environ.setdefault("JWT_SIGNING_KEYS", json.dumps({"test-v1": "T" * 64}))

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core import dependencies
from app.core.rate_limit import RateLimitManager
from app.database.database import Base
from app.models.organization import Organization
from app.models.role import Role
from app.models.user import User


@pytest.fixture(autouse=True)
def local_rate_limit_backend(monkeypatch):
    monkeypatch.setattr(
        dependencies,
        "rate_limit_manager",
        RateLimitManager(redis_url="", app_env="test"),
    )


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    org = Organization(name="Auth Tenant", slug="auth-tenant")
    role = Role(name="ORGANIZATION_OWNER")
    session.add_all([org, role])
    session.commit()
    session.refresh(org)
    session.refresh(role)
    user = User(
        full_name="Test User",
        email="qa@example.com",
        hashed_password="not-used",
        organization_id=org.id,
        role_id=role.id,
        is_active=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    yield session, user, org, role
    session.close()
    Base.metadata.drop_all(bind=engine)


def test_current_user_uses_database_tenant_and_role(monkeypatch, db_session):
    session, user, org, role = db_session
    monkeypatch.setattr(
        dependencies,
        "verify_token",
        lambda _value: {
            "user_id": user.id,
            "token_type": "access",
            "jti": "test-jti",
            "session_version": 0,
            "organization_id": 99999,
            "role_id": 99999,
        },
    )
    request = SimpleNamespace(cookies={}, method="GET", headers={})
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="test")
    current = dependencies.get_current_user(request, credentials, session)
    assert current["organization_id"] == org.id
    assert current["role_id"] == role.id
    assert current["role_name"] == "ORGANIZATION_OWNER"


def test_inactive_user_is_rejected(monkeypatch, db_session):
    session, user, _org, _role = db_session
    user.is_active = False
    session.commit()
    monkeypatch.setattr(
        dependencies,
        "verify_token",
        lambda _value: {"user_id": user.id, "token_type": "access", "jti": "test-jti", "session_version": 0},
    )
    request = SimpleNamespace(cookies={}, method="GET", headers={})
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="test")
    with pytest.raises(HTTPException) as error:
        dependencies.get_current_user(request, credentials, session)
    assert error.value.status_code == 401


def test_stale_session_version_is_rejected(monkeypatch, db_session):
    session, user, _org, _role = db_session
    monkeypatch.setattr(
        dependencies,
        "verify_token",
        lambda _value: {
            "user_id": user.id,
            "token_type": "access",
            "jti": "stale-session",
            "session_version": 1,
        },
    )
    request = SimpleNamespace(cookies={}, method="GET", headers={})
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="stale")
    with pytest.raises(HTTPException) as error:
        dependencies.get_current_user(request, credentials, session)
    assert error.value.status_code == 401


def test_cookie_authenticated_state_change_requires_trusted_origin(db_session):
    session, _user, _org, _role = db_session
    request = SimpleNamespace(
        cookies={"access_token": "cookie-token"},
        method="POST",
        headers={},
    )
    with pytest.raises(HTTPException) as error:
        dependencies.get_current_user(request, None, session)
    assert error.value.status_code == 403
