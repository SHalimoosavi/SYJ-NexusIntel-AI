from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import hash_password
from app.database.database import Base
from app.models.organization import Organization
from app.models.role import Role
from app.models.user import User
from app.services.user_service import authenticate_user

import pytest


@pytest.fixture()
def auth_db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    organization = Organization(name="Enumeration Tenant", slug="enumeration-tenant")
    role = Role(name="ENUMERATION_OWNER")
    session.add_all([organization, role])
    session.commit()
    session.refresh(organization)
    session.refresh(role)
    user = User(
        full_name="Enumeration Test",
        email="known-user@example.invalid",
        hashed_password=hash_password("correct-password-123"),
        organization_id=organization.id,
        role_id=role.id,
        is_active=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    yield session, user
    session.close()
    Base.metadata.drop_all(bind=engine)


def test_unknown_user_and_wrong_password_return_same_authentication_result(auth_db):
    db, user = auth_db
    wrong_password = authenticate_user(
        db,
        user.email,
        "incorrect-password-123",
    )
    unknown_user = authenticate_user(
        db,
        "not-a-real-account@example.invalid",
        "incorrect-password-123",
    )
    assert wrong_password is None
    assert unknown_user is None
