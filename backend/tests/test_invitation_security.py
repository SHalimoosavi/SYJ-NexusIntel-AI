import hashlib

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.database import Base
from app.models.invitation import Invitation
from app.models.organization import Organization
from app.models.role import Role
from app.schemas.invitation import InvitationResponse
from app.services.invitation_service import create_invitation, validate_invitation


def test_invitation_token_is_hashed_at_rest_and_omitted_from_list_schema():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    try:
        organization = Organization(name="Invite Tenant", slug="invite-tenant")
        role = Role(name="VIEWER")
        session.add_all([organization, role])
        session.commit()

        created = create_invitation(
            session,
            organization.id,
            "member@example.invalid",
            role.id,
        )
        stored = session.query(Invitation).filter(
            Invitation.id == created["id"]
        ).one()

        assert stored.token == hashlib.sha256(created["token"].encode()).hexdigest()
        assert stored.token != created["token"]
        assert validate_invitation(session, created["token"]).id == created["id"]
        assert "token" not in InvitationResponse.model_fields
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
