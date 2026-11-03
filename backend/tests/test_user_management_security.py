import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.database import Base
from app.models.organization import Organization
from app.models.role import Role
from app.models.user import User
import app.services.user_management_service as service


@pytest.fixture
def users_db(monkeypatch):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    db = sessionmaker(bind=engine)()
    org = Organization(name="RBAC Tenant", slug="rbac-tenant")
    other_org = Organization(name="Other Tenant", slug="other-tenant")
    roles = {name: Role(name=name) for name in (
        "SUPER_ADMIN", "ORGANIZATION_OWNER", "ADMIN", "MANAGER", "VIEWER"
    )}
    db.add_all([org, other_org, *roles.values()])
    db.commit()
    db.refresh(org)
    db.refresh(other_org)

    def add_user(name, role, organization=org):
        user = User(
            full_name=name,
            email=f"{name.lower().replace(' ', '.')}@example.test",
            hashed_password="test-hash",
            organization_id=organization.id,
            role_id=roles[role].id,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    monkeypatch.setattr(service, "log_event", lambda **_kwargs: None)
    yield db, org, other_org, roles, add_user
    db.close()
    Base.metadata.drop_all(bind=engine)


def test_super_admin_can_change_and_delete_regular_user(users_db):
    db, org, _other, roles, add_user = users_db
    actor = add_user("Root Actor", "SUPER_ADMIN")
    target = add_user("Regular User", "MANAGER")
    updated = service.update_user_status(
        db, target.id, False, org.id, actor.id, "SUPER_ADMIN"
    )
    assert updated.is_active is False
    assert service.delete_user(
        db, target.id, org.id, actor.id, "SUPER_ADMIN"
    ) is True


@pytest.mark.parametrize("operation", ["status", "delete"])
def test_admin_cannot_modify_or_delete_super_admin(users_db, operation):
    db, org, _other, _roles, add_user = users_db
    actor = add_user("Tenant Admin", "ADMIN")
    target = add_user("Root User", "SUPER_ADMIN")
    with pytest.raises(HTTPException) as error:
        if operation == "status":
            service.update_user_status(db, target.id, False, org.id, actor.id, "ADMIN")
        else:
            service.delete_user(db, target.id, org.id, actor.id, "ADMIN")
    assert error.value.status_code == 403


def test_actor_cannot_escalate_own_role(users_db):
    db, org, _other, roles, add_user = users_db
    actor = add_user("Self Actor", "ORGANIZATION_OWNER")
    with pytest.raises(HTTPException) as error:
        service.update_user_role(
            db, actor.id, roles["SUPER_ADMIN"].id, org.id, actor.id, "SUPER_ADMIN"
        )
    assert error.value.status_code == 400


@pytest.mark.parametrize("operation", ["status", "delete"])
def test_last_active_super_admin_cannot_be_disabled_or_deleted(users_db, operation):
    db, org, _other, _roles, add_user = users_db
    actor = add_user("Acting Root", "ORGANIZATION_OWNER")
    target = add_user("Last Root", "SUPER_ADMIN")
    with pytest.raises(HTTPException) as error:
        if operation == "status":
            service.update_user_status(db, target.id, False, org.id, actor.id, "SUPER_ADMIN")
        else:
            service.delete_user(db, target.id, org.id, actor.id, "SUPER_ADMIN")
    assert error.value.status_code == 409
    db.refresh(target)
    assert target.is_active is True


def test_cross_tenant_target_remains_inaccessible(users_db):
    db, org, other_org, _roles, add_user = users_db
    actor = add_user("Tenant Root", "SUPER_ADMIN", org)
    target = add_user("Other Tenant User", "MANAGER", other_org)
    with pytest.raises(HTTPException) as error:
        service.delete_user(db, target.id, org.id, actor.id, "SUPER_ADMIN")
    assert error.value.status_code == 404
    assert db.query(User).filter(User.id == target.id).one()
