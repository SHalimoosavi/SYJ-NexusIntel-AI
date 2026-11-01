"""Tenant boundary regression tests using isolated SQLite data only."""
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.database import Base
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
from app.services.activity_service import create_activity, get_lead_activities
from app.services.agent_memory_service import get_history, get_latest, save_memory
from app.services.audit_dashboard_service import get_audit_logs, get_event_summary
from app.services.invitation_service import get_invitations
from app.services.lead_note_service import create_note, delete_note, get_lead_notes
from app.services.lead_service import delete_lead, get_lead, update_lead_pipeline
from app.services.organization_dashboard_service import get_organization_dashboard
from app.services.organization_service import get_organization, get_organizations
from app.services.subscription_service import get_subscription
from app.services.user_management_service import get_user, get_users


@pytest.fixture()
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
    owner_role = Role(name="ORGANIZATION_OWNER")
    viewer_role = Role(name="VIEWER")
    session.add_all([org_a, org_b, owner_role, viewer_role])
    session.commit()
    session.refresh(org_a)
    session.refresh(org_b)
    session.refresh(owner_role)
    session.refresh(viewer_role)

    user_a = User(
        full_name="Owner A",
        email="owner-a@example.invalid",
        hashed_password="test-hash-a",
        organization_id=org_a.id,
        role_id=owner_role.id,
        is_active=True,
    )
    user_b = User(
        full_name="Owner B",
        email="owner-b@example.invalid",
        hashed_password="test-hash-b",
        organization_id=org_b.id,
        role_id=owner_role.id,
        is_active=True,
    )
    lead_a = Lead(organization_id=org_a.id, business_name="Lead A")
    lead_b = Lead(organization_id=org_b.id, business_name="Lead B")
    session.add_all([user_a, user_b, lead_a, lead_b])
    session.commit()
    for obj in (user_a, user_b, lead_a, lead_b):
        session.refresh(obj)

    session.add_all([
        LeadNote(organization_id=org_a.id, lead_id=lead_a.id, note="A note"),
        LeadNote(organization_id=org_b.id, lead_id=lead_b.id, note="B note"),
        Activity(organization_id=org_a.id, lead_id=lead_a.id, activity_type="CALL"),
        Activity(organization_id=org_b.id, lead_id=lead_b.id, activity_type="CALL"),
        AgentMemory(organization_id=org_a.id, domain="a.example", analysis_data="{}"),
        AgentMemory(organization_id=org_b.id, domain="b.example", analysis_data="{}"),
        AuditLog(organization_id=org_a.id, user_id=user_a.id, event_type="A_EVENT"),
        AuditLog(organization_id=org_b.id, user_id=user_b.id, event_type="B_EVENT"),
        Subscription(organization_id=org_a.id, plan_name="FREE"),
        Subscription(organization_id=org_b.id, plan_name="PRO"),
        Invitation(
            organization_id=org_a.id, email="invite-a@example.invalid",
            role_id=viewer_role.id, token="digest-a", expires_at=__import__("datetime").datetime.utcnow()
        ),
        Invitation(
            organization_id=org_b.id, email="invite-b@example.invalid",
            role_id=viewer_role.id, token="digest-b", expires_at=__import__("datetime").datetime.utcnow()
        ),
    ])
    session.commit()
    yield SimpleNamespace(
        db=session, a=org_a, b=org_b, user_a=user_a, user_b=user_b,
        lead_a=lead_a, lead_b=lead_b, viewer_role=viewer_role,
    )
    session.close()
    Base.metadata.drop_all(bind=engine)


def test_guessed_organization_id_cannot_cross_tenant(tenant_db):
    db, a, b = tenant_db.db, tenant_db.a, tenant_db.b
    assert get_organization(db, b.id, a.id) is None
    assert [row.id for row in get_organizations(db, a.id)] == [a.id]


def test_guessed_lead_id_cannot_be_read_updated_or_deleted(tenant_db):
    db, a, b, lead_b = tenant_db.db, tenant_db.a, tenant_db.b, tenant_db.lead_b
    assert get_lead(db, lead_b.id, a.id) is None
    update = SimpleNamespace(
        status="WON", pipeline_stage="WON", estimated_value=100,
        probability=100, actual_revenue=100, last_contacted=None, next_followup=None,
    )
    assert update_lead_pipeline(db, lead_b.id, update, a.id) is None
    assert delete_lead(db, lead_b.id, a.id) is False
    assert db.query(Lead).filter(Lead.id == lead_b.id, Lead.organization_id == b.id).one()


def test_guessed_lead_id_cannot_be_used_to_create_notes_or_activities(tenant_db):
    db, a, lead_b = tenant_db.db, tenant_db.a, tenant_db.lead_b
    with pytest.raises(HTTPException) as note_error:
        create_note(db, SimpleNamespace(lead_id=lead_b.id, note="attack", note_type="GENERAL"), a.id)
    assert note_error.value.status_code == 404
    with pytest.raises(HTTPException) as activity_error:
        create_activity(db, SimpleNamespace(lead_id=lead_b.id, activity_type="CALL", description="attack"), a.id)
    assert activity_error.value.status_code == 404


def test_guessed_note_id_cannot_be_read_or_deleted(tenant_db):
    db, a, b = tenant_db.db, tenant_db.a, tenant_db.b
    note_b = db.query(LeadNote).filter(LeadNote.organization_id == b.id).one()
    assert get_lead_notes(db, tenant_db.lead_b.id, a.id) == []
    with pytest.raises(HTTPException) as error:
        delete_note(db, note_b.id, a.id)
    assert error.value.status_code == 404
    assert db.query(LeadNote).filter(LeadNote.id == note_b.id).one()


def test_guessed_activity_id_and_lead_id_do_not_return_other_tenant_data(tenant_db):
    db, a, b = tenant_db.db, tenant_db.a, tenant_db.b
    assert get_lead_activities(db, tenant_db.lead_b.id, a.id) == []
    activity_b = db.query(Activity).filter(Activity.organization_id == b.id).one()
    assert activity_b.organization_id == b.id


def test_user_idor_is_scoped_for_read_and_list(tenant_db):
    db, a, b = tenant_db.db, tenant_db.a, tenant_db.b
    assert get_user(db, tenant_db.user_b.id, a.id) is None
    assert [u.id for u in get_users(db, a.id)] == [tenant_db.user_a.id]


def test_agent_memory_history_and_latest_are_tenant_scoped(tenant_db):
    db, a = tenant_db.db, tenant_db.a
    assert get_history(db, "b.example", a.id) == []
    assert get_latest(db, "b.example", a.id) is None
    saved = save_memory(db, {"domain": "new.example", "overall_score": 10, "analysis_data": {}}, a.id)
    assert saved.organization_id == a.id


def test_subscription_and_invitation_reads_are_tenant_scoped(tenant_db):
    db, a, b = tenant_db.db, tenant_db.a, tenant_db.b
    assert get_subscription(db, a.id).plan_name == "FREE"
    assert get_subscription(db, a.id).organization_id != b.id
    assert [item.email for item in get_invitations(db, a.id)] == ["invite-a@example.invalid"]


def test_audit_logs_and_summaries_are_tenant_scoped(tenant_db):
    db, a = tenant_db.db, tenant_db.a
    assert {row.event_type for row in get_audit_logs(db, a.id)} == {"A_EVENT"}
    assert get_event_summary(db, a.id) == {"A_EVENT": 1}


def test_organization_dashboard_counts_only_own_tenant(tenant_db):
    db, a = tenant_db.db, tenant_db.a
    summary = get_organization_dashboard(db, a.id)
    assert summary["users"] == 1
    assert summary["leads"] == 1
    assert summary["invitations"] == 1


def test_audit_rows_are_append_only_through_orm(tenant_db):
    db, a = tenant_db.db, tenant_db.a
    audit = db.query(AuditLog).filter(AuditLog.organization_id == a.id).one()
    audit.description = "tampered"
    with pytest.raises(ValueError, match="append-only"):
        db.flush()
    db.rollback()
    audit = db.query(AuditLog).filter(AuditLog.organization_id == a.id).one()
    with pytest.raises(ValueError, match="append-only"):
        db.delete(audit)
        db.flush()


def test_sensitive_note_and_activity_mutations_are_audited_with_actor(tenant_db):
    db, org, user, lead = tenant_db.db, tenant_db.a, tenant_db.user_a, tenant_db.lead_a
    create_note(
        db,
        SimpleNamespace(lead_id=lead.id, note="Audit test note", note_type="GENERAL"),
        org.id,
        user.id,
    )
    create_activity(
        db,
        SimpleNamespace(lead_id=lead.id, activity_type="CALL", description="Audit test"),
        org.id,
        user.id,
    )
    rows = get_audit_logs(db, org.id)
    actor_events = {
        (row.event_type, row.user_id)
        for row in rows
    }
    assert ("LEAD_NOTE_CREATED", user.id) in actor_events
    assert ("ACTIVITY_CREATED", user.id) in actor_events
