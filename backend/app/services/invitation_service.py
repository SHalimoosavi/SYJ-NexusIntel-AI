from datetime import datetime, timedelta
import hashlib
import secrets

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.invitation import Invitation
from app.models.user import User
from app.models.role import Role
from app.core.security import hash_password
from app.services.audit_service import log_event

INVITATION_EXPIRY_HOURS = 72


def generate_invitation_token() -> str:
    return secrets.token_urlsafe(32)


def _token_digest(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_invitation(
    db: Session,
    organization_id: int,
    email: str,
    role_id: int,
    actor_role_name: str = "ORGANIZATION_OWNER",
    actor_user_id: int | None = None,
):
    target_role = db.query(Role).filter(Role.id == role_id).first()
    if target_role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    allowed_for_owner = {"MANAGER", "SALES_REPRESENTATIVE", "VIEWER"}
    allowed_for_manager = {"SALES_REPRESENTATIVE", "VIEWER"}
    if actor_role_name == "ORGANIZATION_OWNER" and target_role.name not in allowed_for_owner:
        raise HTTPException(status_code=403, detail="Role assignment is not permitted")
    if actor_role_name == "MANAGER" and target_role.name not in allowed_for_manager:
        raise HTTPException(status_code=403, detail="Role assignment is not permitted")
    if actor_role_name not in {"SUPER_ADMIN", "ORGANIZATION_OWNER", "MANAGER"}:
        raise HTTPException(status_code=403, detail="Invitation creation is not permitted")

    normalized_email = email.strip().lower()
    existing = (
        db.query(Invitation)
        .filter(
            Invitation.email == normalized_email,
            Invitation.organization_id == organization_id,
            Invitation.is_used.is_(False),
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Active invitation already exists")

    raw_token = generate_invitation_token()
    invitation = Invitation(
        organization_id=organization_id,
        email=normalized_email,
        role_id=role_id,
        token=_token_digest(raw_token),
        expires_at=datetime.utcnow() + timedelta(hours=INVITATION_EXPIRY_HOURS),
    )
    db.add(invitation)
    db.commit()
    db.refresh(invitation)

    log_event(
        db=db,
        organization_id=organization_id,
        user_id=actor_user_id,
        event_type="INVITATION_CREATED",
        resource_type="INVITATION",
        resource_id=invitation.id,
        description="Invitation created",
    )

    # Raw bearer token is returned exactly once and is never stored in the DB.
    return {
        "id": invitation.id,
        "organization_id": invitation.organization_id,
        "email": invitation.email,
        "role_id": invitation.role_id,
        "is_used": invitation.is_used,
        "token": raw_token,
    }


def validate_invitation(db: Session, token: str):
    invitation = (
        db.query(Invitation)
        .filter(Invitation.token == _token_digest(token))
        .first()
    )
    if not invitation:
        raise HTTPException(status_code=400, detail="Invalid or expired invitation")
    if invitation.is_used or invitation.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invalid or expired invitation")
    return invitation


def accept_invitation(
    db: Session,
    full_name: str,
    email: str,
    password: str,
    invitation_token: str,
):
    invitation = validate_invitation(db, invitation_token)
    normalized_email = email.strip().lower()
    if invitation.email.lower() != normalized_email:
        raise HTTPException(status_code=400, detail="Invalid or expired invitation")

    existing_user = (
        db.query(User)
        .filter(User.email == normalized_email)
        .first()
    )
    if existing_user:
        raise HTTPException(status_code=400, detail="Unable to accept invitation")

    user = User(
        full_name=full_name.strip(),
        email=normalized_email,
        hashed_password=hash_password(password),
        organization_id=invitation.organization_id,
        role_id=invitation.role_id,
        is_active=True,
    )
    db.add(user)
    invitation.is_used = True
    db.commit()
    db.refresh(user)

    log_event(
        db=db,
        organization_id=invitation.organization_id,
        user_id=user.id,
        event_type="INVITATION_ACCEPTED",
        resource_type="USER",
        resource_id=user.id,
        description="Organization invitation accepted",
    )
    return user


def get_invitations(db: Session, organization_id: int):
    return (
        db.query(Invitation)
        .filter(Invitation.organization_id == organization_id)
        .order_by(Invitation.id.desc())
        .all()
    )
