from datetime import datetime, timedelta

import pytest
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


@pytest.fixture()
def tenant_client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    factory = sessionmaker(bind=engine)
    db = factory()

    org_a = Organization(name="HTTP Tenant A", slug="http-tenant-a")
    org_b = Organization(name="HTTP Tenant B", slug="http-tenant-b")
    owner_role = Role(name="ORGANIZATION_OWNER")
    viewer_role = Role(name="VIEWER")
    manager_role = Role(name="MANAGER")
    db.add_all([org_a, org_b, owner_role, viewer_role, manager_role])
    db.commit()
    for item in (org_a, org_b, owner_role, viewer_role, manager_role):
        db.refresh(item)

    user_a = User(
        full_name="HTTP Owner A",
        email="http-owner-a@example.invalid",
        hashed_password="test-hash-a",
        organization_id=org_a.id,
        role_id=owner_role.id,
        is_active=True,
    )
    user_b = User(
        full_name="HTTP Owner B",
        email="http-owner-b@example.invalid",
        hashed_password="test-hash-b",
        organization_id=org_b.id,
        role_id=owner_role.id,
        is_active=True,
    )
    lead_a = Lead(
        organization_id=org_a.id,
        business_name="HTTP Lead A",
        estimated_value=100,
        pipeline_stage="NEW",
    )
    lead_b = Lead(
        organization_id=org_b.id,
        business_name="HTTP Lead B",
        estimated_value=900,
        pipeline_stage="WON",
    )
    db.add_all([user_a, user_b, lead_a, lead_b])
    db.commit()
    for item in (user_a, user_b, lead_a, lead_b):
        db.refresh(item)

    note_a = LeadNote(
        organization_id=org_a.id, lead_id=lead_a.id, note="Tenant A note"
    )
    note_b = LeadNote(
        organization_id=org_b.id, lead_id=lead_b.id, note="Tenant B note"
    )
    activity_a = Activity(
        organization_id=org_a.id, lead_id=lead_a.id, activity_type="CALL"
    )
    activity_b = Activity(
        organization_id=org_b.id, lead_id=lead_b.id, activity_type="CALL"
    )
    memory_a = AgentMemory(
        organization_id=org_a.id, domain="a.example", analysis_data="{}"
    )
    memory_b = AgentMemory(
        organization_id=org_b.id, domain="b.example", analysis_data="{}"
    )
    audit_a = AuditLog(
        organization_id=org_a.id, user_id=user_a.id, event_type="TENANT_A_EVENT"
    )
    audit_b = AuditLog(
        organization_id=org_b.id, user_id=user_b.id, event_type="TENANT_B_EVENT"
    )
    invitation_a = Invitation(
        organization_id=org_a.id, email="a-invite@example.invalid",
        role_id=viewer_role.id, token="a-http-invite-token",
        expires_at=datetime.utcnow() + timedelta(days=1),
    )
    invitation_b = Invitation(
        organization_id=org_b.id, email="b-invite@example.invalid",
        role_id=viewer_role.id, token="b-http-invite-token",
        expires_at=datetime.utcnow() + timedelta(days=1),
    )
    subscription_a = Subscription(
        organization_id=org_a.id, plan_name="FREE",
        max_users=3, max_leads=100, max_ai_requests=100,
    )
    subscription_b = Subscription(
        organization_id=org_b.id, plan_name="PRO",
        max_users=20, max_leads=1000, max_ai_requests=1000,
    )
    db.add_all([
        note_a, note_b, activity_a, activity_b, memory_a, memory_b,
        audit_a, audit_b, invitation_a, invitation_b,
        subscription_a, subscription_b,
    ])
    db.commit()

    current_user = {
        "user_id": user_a.id,
        "sub": user_a.email,
        "organization_id": org_a.id,
        "role_id": owner_role.id,
        "role_name": "ORGANIZATION_OWNER",
    }

    def override_db():
        session = factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_user] = lambda: current_user

    with TestClient(app) as client:
        yield {
            "client": client,
            "a": org_a,
            "b": org_b,
            "user_a": user_a,
            "user_b": user_b,
            "lead_a": lead_a,
            "lead_b": lead_b,
        }

    app.dependency_overrides.clear()
    db.close()
    Base.metadata.drop_all(bind=engine)


def test_http_lead_list_and_guessed_id_mutations_are_tenant_scoped(tenant_client):
    client = tenant_client["client"]
    lead_b = tenant_client["lead_b"]
    response = client.get("/leads")
    assert response.status_code == 200
    assert [lead["business_name"] for lead in response.json()] == ["HTTP Lead A"]

    update = {
        "status": "WON",
        "pipeline_stage": "WON",
        "estimated_value": 900,
        "probability": 100,
        "actual_revenue": 900,
    }
    assert client.put(f"/leads/{lead_b.id}", json=update).status_code == 404
    assert client.delete(f"/leads/{lead_b.id}").status_code == 404


def test_http_notes_and_activities_reject_cross_tenant_parent_and_ids(tenant_client):
    client = tenant_client["client"]
    lead_b = tenant_client["lead_b"]

    assert client.get(f"/lead-notes/{lead_b.id}").json() == []
    assert client.get(f"/activities/{lead_b.id}").json() == []

    note = {"lead_id": lead_b.id, "note": "cross tenant", "note_type": "GENERAL"}
    activity = {"lead_id": lead_b.id, "activity_type": "CALL", "description": "cross tenant"}
    assert client.post("/lead-notes", json=note).status_code == 404
    assert client.post("/activities", json=activity).status_code == 404


def test_http_user_organization_subscription_and_invitation_idor(tenant_client):
    client = tenant_client["client"]
    user_b = tenant_client["user_b"]
    org_b = tenant_client["b"]

    user_list = client.get("/users")
    assert user_list.status_code == 200
    assert [row["email"] for row in user_list.json()] == ["http-owner-a@example.invalid"]
    assert client.get(f"/users/{user_b.id}").status_code == 404
    assert client.put(
        f"/users/{user_b.id}/status",
        json={"is_active": False},
    ).status_code == 404
    assert client.put(
        f"/users/{user_b.id}/role",
        json={"role_id": 2},
    ).status_code == 404
    assert client.delete(f"/users/{user_b.id}").status_code == 404
    organization_list = client.get("/organizations")
    assert organization_list.status_code == 200
    assert [row["slug"] for row in organization_list.json()] == ["http-tenant-a"]
    assert client.get(f"/organizations/{org_b.id}").status_code == 404
    assert client.get(f"/subscriptions/{tenant_client["a"].id}").status_code == 200
    assert client.get(f"/subscriptions/{org_b.id}").status_code == 404

    invitations = client.get("/invitations")
    assert invitations.status_code == 200
    assert [item["email"] for item in invitations.json()] == ["a-invite@example.invalid"]


def test_http_audit_and_memory_queries_do_not_return_other_tenant_rows(tenant_client):
    client = tenant_client["client"]

    audit = client.get("/audit/logs")
    assert audit.status_code == 200
    assert {row["event_type"] for row in audit.json()} == {"TENANT_A_EVENT"}

    events = client.get("/audit/events")
    assert events.status_code == 200
    assert events.json() == {"TENANT_A_EVENT": 1}

    history = client.get("/agent-memory/history/b.example")
    assert history.status_code == 200
    assert history.json() == []

    latest = client.get("/agent-memory/latest/b.example")
    assert latest.status_code == 200
    assert latest.json() is None


def test_http_dashboard_and_analytics_use_only_current_tenant(tenant_client):
    client = tenant_client["client"]

    org_dashboard = client.get("/organization-dashboard")
    assert org_dashboard.status_code == 200
    assert org_dashboard.json()["users"] == 1
    assert org_dashboard.json()["leads"] == 1
    assert org_dashboard.json()["invitations"] == 1

    crm = client.get("/crm/stats")
    assert crm.status_code == 200
    assert crm.json()["total_leads"] == 1

    revenue = client.get("/crm/revenue")
    assert revenue.status_code == 200
    assert revenue.json()["pipeline_value"] == 100

    pipeline = client.get("/crm/pipeline")
    assert pipeline.status_code == 200
    assert pipeline.json()["new"] == 1
    assert pipeline.json()["won"] == 0

    executive = client.get("/dashboard/executive")
    assert executive.status_code == 200
    assert executive.json()["leads"] == 1
    assert executive.json()["crm"]["total_leads"] == 1

    relationship = client.get("/relationship-intelligence")
    assert relationship.status_code == 200
    assert relationship.json()["total_leads"] == 1

    forecast = client.get("/revenue-forecast/dashboard")
    assert forecast.status_code == 200
    assert forecast.json()["pipeline_value"] == 100

    priorities = client.get("/sales-agent/priorities")
    assert priorities.status_code == 200
    assert [item["business_name"] for item in priorities.json()] == ["HTTP Lead A"]


def test_http_rbac_prevents_owner_from_using_super_admin_routes(tenant_client):
    client = tenant_client["client"]
    org_b = tenant_client["b"]

    assert client.get("/subscriptions").status_code == 403
    assert client.post(
        "/subscriptions",
        json={"organization_id": org_b.id, "plan_name": "PRO"},
    ).status_code == 403
    assert client.post(
        "/organizations",
        json={"name": "Unauthorized", "slug": "unauthorized"},
    ).status_code == 403


def test_http_viewer_cannot_bypass_owner_or_admin_routes(tenant_client):
    viewer = {
        "user_id": tenant_client["user_a"].id,
        "sub": tenant_client["user_a"].email,
        "organization_id": tenant_client["a"].id,
        "role_id": 2,
        "role_name": "VIEWER",
    }
    app.dependency_overrides[get_current_user] = lambda: viewer
    client = tenant_client["client"]

    assert client.get("/users").status_code == 403
    assert client.get("/audit/logs").status_code == 403
    assert client.post(
        "/invitations",
        json={"email": "attacker@example.invalid", "role_id": 2},
    ).status_code == 403
    assert client.get(f"/organizations/{tenant_client['a'].id}").status_code == 200
