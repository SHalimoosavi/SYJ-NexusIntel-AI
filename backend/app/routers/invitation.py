from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.invitation import (
    InvitationCreate,
    InvitationAccept,
    InvitationResponse,
    InvitationCreatedResponse,
    InvitationAcceptResponse,
)
from app.services.invitation_service import (
    create_invitation,
    accept_invitation,
    get_invitations,
)
from app.core.rbac import require_roles

router = APIRouter(prefix="/invitations", tags=["Invitations"])


@router.post("", response_model=InvitationCreatedResponse)
def create_invitation_route(
    invitation: InvitationCreate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(["SUPER_ADMIN", "ORGANIZATION_OWNER", "MANAGER"])
    ),
):
    return create_invitation(
        db=db,
        organization_id=current_user["organization_id"],
        email=invitation.email,
        role_id=invitation.role_id,
        actor_role_name=current_user["role_name"],
        actor_user_id=current_user["user_id"],
    )


@router.get("", response_model=list[InvitationResponse])
def get_invitations_route(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(["SUPER_ADMIN", "ORGANIZATION_OWNER", "MANAGER"])
    ),
):
    return get_invitations(db, current_user["organization_id"])


@router.post("/accept", response_model=InvitationAcceptResponse)
def accept_invitation_route(
    request: InvitationAccept,
    db: Session = Depends(get_db),
):
    accept_invitation(
        db=db,
        full_name=request.full_name,
        email=request.email,
        password=request.password,
        invitation_token=request.invitation_token,
    )
    return {"success": True}
