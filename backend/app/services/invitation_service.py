from datetime import datetime
from datetime import timedelta
import secrets

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.invitation import Invitation
from app.models.user import User

from app.core.security import hash_password

from app.services.audit_service import (
    log_event,
)


INVITATION_EXPIRY_HOURS = 72


def generate_invitation_token():
    return secrets.token_urlsafe(32)


def create_invitation(
    db: Session,
    organization_id: int,
    email: str,
    role_id: int,
):
    existing = (
        db.query(Invitation)
        .filter(
            Invitation.email == email,
            Invitation.organization_id == organization_id,
            Invitation.is_used == False,
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Active invitation already exists",
        )

    invitation = Invitation(
        organization_id=organization_id,
        email=email,
        role_id=role_id,
        token=generate_invitation_token(),
        expires_at=(
            datetime.utcnow()
            + timedelta(
                hours=INVITATION_EXPIRY_HOURS
            )
        ),
    )

    db.add(invitation)

    db.commit()

    db.refresh(invitation)

    log_event(
        db=db,
        organization_id=organization_id,
        user_id=None,
        event_type="INVITATION_CREATED",
        resource_type="INVITATION",
        resource_id=invitation.id,
        description=f"Invitation created for {email}",
    )

    return invitation


def validate_invitation(
    db: Session,
    token: str,
):
    invitation = (
        db.query(Invitation)
        .filter(
            Invitation.token == token
        )
        .first()
    )

    if not invitation:
        raise HTTPException(
            status_code=404,
            detail="Invitation not found",
        )

    if invitation.is_used:
        raise HTTPException(
            status_code=400,
            detail="Invitation already used",
        )

    if invitation.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=400,
            detail="Invitation expired",
        )

    return invitation


def accept_invitation(
    db: Session,
    full_name: str,
    email: str,
    password: str,
    invitation_token: str,
):
    invitation = validate_invitation(
        db,
        invitation_token,
    )

    if (
        invitation.email.lower()
        != email.lower()
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "Invitation email mismatch"
            ),
        )

    existing_user = (
        db.query(User)
        .filter(
            User.email == email
        )
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail=(
                "User already exists"
            ),
        )

    user = User(
        full_name=full_name,
        email=email,
        hashed_password=hash_password(
            password
        ),
        organization_id=
        invitation.organization_id,
        role_id=invitation.role_id,
        is_active=True,
    )

    db.add(user)

    invitation.is_used = True

    db.commit()

    db.refresh(user)

    log_event(
        db=db,
        organization_id=
        invitation.organization_id,
        user_id=user.id,
        event_type=
        "INVITATION_ACCEPTED",
        resource_type="USER",
        resource_id=user.id,
        description=(
            f"User joined via invitation: "
            f"{email}"
        ),
    )

    return user


def get_invitations(
    db: Session,
    organization_id: int,
):
    return (
        db.query(Invitation)
        .filter(
            Invitation.organization_id
            == organization_id
        )
        .order_by(
            Invitation.id.desc()
        )
        .all()
    )
