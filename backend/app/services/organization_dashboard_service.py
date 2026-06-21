from sqlalchemy.orm import Session

from app.models.organization import Organization
from app.models.user import User
from app.models.lead import Lead
from app.models.invitation import Invitation


def get_organization_dashboard(
    db: Session,
    organization_id: int,
):
    organization = (
        db.query(Organization)
        .filter(
            Organization.id == organization_id
        )
        .first()
    )

    users = (
        db.query(User)
        .filter(
            User.organization_id
            == organization_id
        )
        .count()
    )

    leads = (
        db.query(Lead)
        .filter(
            Lead.organization_id
            == organization_id
        )
        .count()
    )

    invitations = (
        db.query(Invitation)
        .filter(
            Invitation.organization_id
            == organization_id
        )
        .count()
    )

    return {
        "organization": (
            organization.name
            if organization
            else None
        ),
        "plan": (
            organization.plan
            if organization
            else None
        ),
        "users": users,
        "leads": leads,
        "invitations": invitations,
    }
