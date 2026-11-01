"""Tenant boundary regression tests using isolated SQLite data only."""
from datetime import datetime, timedelta
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.dependencies import get_current_user
from app.database.database import Base, get_db
from app.main import app
from app.models.activity import Activity
from app.models.agent_memory import AgentMemory
from app.models.audit_log import AuditLog
from app.models.invitation import Invitation
from app.models.lead import Lead
from app.models.lead_note import LeadNote
from app.models.organization import Organization
from app.models.role import Role
from app.models.subscription import Subscription
from app.models.user import User
from app.services.activity_service import (
    create_activity,
    create_system_activity,
    get_lead_activities,
)
from app.services.agent_memory_service import get_history, get_latest
from app.services.audit_dashboard_service import get_audit_logs, get_event_summary
from app.services.invitation_service import get_invitations
from app.services.lead_note_service import create_note, delete_note, get_lead_notes
from app.services.lead_service import delete_lead, get_all_leads, get_lead, update_lead_pipeline
from app.services.organization_service import get_organization, get_organizations
from app.services.subscription_service import get_subscription
from app.services.user_management_service import get_user, get_users, update_user_role


@pytest.fixture
def tenant_db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()

    org_a = Organization(name="Tenant A", slug="tenant-a")
    org_b = Organization(name="Tenant B", slug="tenant-b")
    owner = Role(name="ORGANIZATION_OWNER")
    manager = Role(name="MANAGER")
    session.add_all([org_a, org_b, owner, manager])
    session.commit()
    for item in (org_a, org_b, owner, manager):
        session.refresh(item)

    user_a = User(
        full_name="Owner A",
        email="owner-a@example.invalid",
        hashed_password="test-hash",
        organization_id=org_a.id,
        role_id=owner.id,
        is_active=True,
    )
    user_b = User(
        full_name="Owner B",
        email="owner-b@example.invalid",
        hashed_password="test-hash",
        organization_id=org_b.id,
        role_id=owner.id,
        is_active=True,
    )
    lead_a = Lead(organization_id=org_a.id, business_name="Lead A")
    lead_b = Lead(organization_id=org_b.id, business_name="Lead B")
    session.add_all([user_a, user_b, lead_a, lead_b])
    session.commit()
    for item in (user_a, user_b, lead_a, lead_b):
        session.refresh(item)

    note_a = LeadNote(organization_id=org_a.id, lead_id=lead_a.id, note="A private note")
    note_b = LeadNote(organization_id=org_b.id, lead_id=lead_b.id, note="B private note")
    activity_a = Activity(
        organization_id=org_a.id,
        lead_id=lead_a.id,
        activity_type="CALL",
        description="A activity",
    )
    activity_b = Activity(
        organization_id=org_b.id,
        lead_id=lead_b.id,
        activity_type="CALL",
        description="B activity",
    )
    memory_a = AgentMemory(
        organization_id=org_a.id,
        domain="a.example",
        overall_score=80,
        priority="HOT",
        estimated_value="100",
        analysis_data='{"tenant":"A"}',
    )
    memory_b = AgentMemory(
        organization_id=org_b.id,
        domain="a.example",
        overall_score=90,
        priority="HOT",
        estimated_value="200",
        analysis_data='{"tenant":"B"}',
    )
    audit_a = AuditLog(
        organization_id=org_a.id,
        user_id=user_a.id,
        event_type="A_EVENT",
        description="A event",
    )
    audit_b = AuditLog(
        organization_id=org_b.id,
        user_id=user_b.id,
        event_type="B_EVENT",
        description="B event",
    )
    subscription_a = Subscription(organization_id=org_a.id, plan_name="FREE")
    subscription_b = Subscription(organization_id=org_b.id, plan_name="FREE")
    invitation_a = Invitation(
        organization_id=org_a.id,
        email="invite-a@example.invalid",
        role_id=manager.id,
        token="digest-a",
        expires_at=datetime.utcnow() + timedelta(hours=1),
    )
    invitation_b = Invitation(
        organization_id=org_b.id,
        email="invite-b@example.invalid",
        role_id=manager.id,
        token="digest-b",
        expires_at=datetime.utcnow() + timedelta(hours=1),
    )
    session.add_all([
        note_a, note_b, activity_a, activity_b, memory_a, memory_b,
        audit_a, audit_b, subscription_a, subscription_b,
        invitation_a, invitation_b,
    ])
    session.commit()
    for item in (
        note_a, note_b, activity_a, activity_b, memory_a, memory_b,
        audit_a, audit_b, subscription_a, subscription_b,
        invitation_a, invitation_b,
    ):
        session.refresh(item)

    yield {
        "db": session,
        "org_a": org_a,
        "org_b": org_b,
        "owner": owner,
        "manager": manager,
        "user_a": user_a,
        "user_b": user_b,
        "lead_a": lead_a,
        "lead_b": lead_b,
        "note_a": note_a,
        "note_b": note_b,
        "memory_a": memory_a,
        "memory_b": memory_b,
        "audit_a": audit_a,
        "audit_b": audit_b,
        "invitation_a": invitation_a,
        "invitation_b": invitation_b,
    }
    session.close()
    Base.metadata.drop_all(bind=engine)


def test_organization_queries_are_scoped_to_tenant(tenant_db):
    db = tenant_db["db"]
    org_a, org_b = tenant_db["org_a"], tenant_db["org_b"]
    assert [row.id for row in get_organizations(db, org_a.id)] == [org_a.id]
    assert get_organization(db, org_b.id, org_a.id) is None
    assert get_organization(db, org_a.id, org_a.id).id == org_a.id


def test_lead_reads_updates_and_deletes_cannot_cross_tenant(tenant_db):
    db, lead_a, lead_b = tenant_db["db"], tenant_db["lead_a"], tenant_db["lead_b"]
    assert [row.id for row in get_all_leads(db, tenant_db["org_a"].id)] == [lead_a.id]
    assert get_lead(db, lead_b.id, tenant_db["org_a"].id) is None
    update = SimpleNamespace(
        status="WON",
        pipeline_stage="CLOSED",
        estimated_value=100,
        probability=100,
        actual_revenue=100,
        last_contacted=None,
        next_followup=None,
    )
    assert update_lead_pipeline(db, lead_b.id, update, tenant_db["org_a"].id) is None
    assert delete_lead(db, lead_b.id, tenant_db["org_a"].id) is False
    assert db.query(Lead).filter(Lead.id == lead_b.id).one().business_name == "Lead B"


def test_notes_and_activities_are_tenant_scoped(tenant_db):
    db, org_a, lead_b, note_b = (
        tenant_db["db"],
        tenant_db["org_a"],
        tenant_db["lead_b"],
        tenant_db["note_b"],
    )
    assert get_lead_notes(db, lead_b.id, org_a.id) == []
    with pytest.raises(HTTPException) as create_error:
        create_note(db, SimpleNamespace(lead_id=lead_b.id, note="attack", note_type="GENERAL"), org_a.id)
    assert create_error.value.status_code == 404
    with pytest.raises(HTTPException):
        delete_note(db, note_b.id, org_a.id)
    assert get_lead_activities(db, lead_b.id, org_a.id) == []
    with pytest.raises(HTTPException) as activity_error:
        create_activity(
            db,
            SimpleNamespace(lead_id=lead_b.id, activity_type="CALL", description="attack"),
            org_a.id,
        )
    assert activity_error.value.status_code == 404
    with pytest.raises(HTTPException) as system_activity_error:
        create_system_activity(db, lead_b.id, "SYSTEM", "attack", org_a.id)
    assert system_activity_error.value.status_code == 404


def test_agent_memory_audit_invitation_and_subscription_are_scoped(tenant_db):
    db, org_a, org_b = tenant_db["db"], tenant_db["org_a"], tenant_db["org_b"]
    assert [row.id for row in get_history(db, "a.example", org_a.id)] == [tenant_db["memory_a"].id]
    assert get_latest(db, "a.example", org_a.id).id == tenant_db["memory_a"].id
    assert [row.event_type for row in get_audit_logs(db, org_a.id)] == ["A_EVENT"]
    assert get_event_summary(db, org_a.id) == {"A_EVENT": 1}
    assert [row.id for row in get_invitations(db, org_a.id)] == [tenant_db["invitation_a"].id]
    assert get_subscription(db, org_a.id).organization_id == org_a.id
    assert get_subscription(db, org_b.id).organization_id == org_b.id


def test_user_management_cannot_read_or_modify_other_tenant(tenant_db):
    db, org_a, user_b = tenant_db["db"], tenant_db["org_a"], tenant_db["user_b"]
    assert [row.id for row in get_users(db, org_a.id)] == [tenant_db["user_a"].id]
    assert get_user(db, user_b.id, org_a.id) is None
    with pytest.raises(HTTPException) as error:
        update_user_role(
            db,
            user_b.id,
            tenant_db["manager"].id,
            org_a.id,
            tenant_db["user_a"].id,
            "ORGANIZATION_OWNER",
        )
    assert error.value.status_code == 404
    assert db.query(User).filter(User.id == user_b.id).one().role_id == tenant_db["owner"].id


def test_api_routes_require_authentication_except_explicit_public_routes():
    from fastapi.routing import APIRoute

    public = {
        ("GET", "/"),
        ("GET", "/health"),
        ("POST", "/auth/login"),
        ("POST", "/auth/refresh"),
        ("POST", "/auth/logout"),
        ("POST", "/invitations/accept"),
    }

    def dependency_calls(dependant):
        for child in dependant.dependencies:
            yield child.call
            yield from dependency_calls(child)

    missing = []
    for route in app.routes:
        if not isinstance(route, APIRoute) or not route.include_in_schema:
            continue
        for method in route.methods or set():
            if (method, route.path) in public:
                continue
            if get_current_user not in set(dependency_calls(route.dependant)):
                missing.append(f"{method} {route.path}")
    assert missing == []


def test_api_idor_guessed_ids_are_blocked_for_tenant_a(tenant_db):
    db = tenant_db["db"]
    org_a = tenant_db["org_a"]
    user_a = tenant_db["user_a"]
    current_user = {
        "user_id": user_a.id,
        "sub": user_a.email,
        "organization_id": org_a.id,
        "role_id": tenant_db["owner"].id,
        "role_name": "ORGANIZATION_OWNER",
    }

    def override_db():
        yield db

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_user] = lambda: current_user
    try:
        client = TestClient(app)
        lead_b_id = tenant_db["lead_b"].id
        note_b_id = tenant_db["note_b"].id
        user_b_id = tenant_db["user_b"].id
        org_b_id = tenant_db["org_b"].id

        payload = {
            "status": "WON",
            "pipeline_stage": "CLOSED",
            "estimated_value": 100,
            "probability": 100,
            "actual_revenue": 100,
        }
        assert client.put(f"/leads/{lead_b_id}", json=payload).status_code == 404
        assert client.delete(f"/leads/{lead_b_id}").status_code == 404
        assert client.get(f"/lead-notes/{lead_b_id}").json() == []
        assert client.delete(f"/lead-notes/{note_b_id}").status_code in {403, 404}
        assert client.get(f"/activities/{lead_b_id}").json() == []
        assert client.get(f"/users/{user_b_id}").status_code == 404
        assert client.get(f"/organizations/{org_b_id}").status_code == 404
        assert client.get(f"/subscriptions/{org_b_id}").status_code == 404

        audit_response = client.get("/audit/logs")
        assert audit_response.status_code == 200
        assert all(row["event_type"] == "A_EVENT" for row in audit_response.json())
        invitation_response = client.get("/invitations")
        assert invitation_response.status_code == 200
        assert all(row["organization_id"] == org_a.id for row in invitation_response.json())
        memory_response = client.get("/agent-memory/history/a.example")
        assert memory_response.status_code == 200
        assert all(row["id"] == tenant_db["memory_a"].id for row in memory_response.json())
    finally:
        app.dependency_overrides.clear()
