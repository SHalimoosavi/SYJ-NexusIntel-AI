from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.schemas.invitation import (
    InvitationCreate,
    InvitationAccept,
    InvitationResponse,
)

from app.services.invitation_service import (
    create_invitation,
    accept_invitation,
    get_invitations,
)

from app.core.dependencies import (
    get_current_user,
)

from app.core.rbac import (
    require_roles,
)

router = APIRouter(
    prefix="/invitations",
    tags=["Invitations"],
)


@router.post(
    "",
    response_model=InvitationResponse,
)
def create_invitation_route(
    invitation: InvitationCreate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            [
                "SUPER_ADMIN",
                "ORGANIZATION_OWNER",
                "MANAGER",
            ]
        )
    ),
):
    return create_invitation(
        db=db,
        organization_id=current_user[
            "organization_id"
        ],
        email=invitation.email,
        role_id=invitation.role_id,
    )


@router.get(
    "",
    response_model=list[InvitationResponse],
)
def get_invitations_route(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            [
                "SUPER_ADMIN",
                "ORGANIZATION_OWNER",
                "MANAGER",
            ]
        )
    ),
):
    return get_invitations(
        db,
        current_user[
            "organization_id"
        ],
    )


@router.post(
    "/accept",
)
def accept_invitation_route(
    request: InvitationAccept,
    db: Session = Depends(get_db),
):
    user = accept_invitation(
        db=db,
        full_name=request.full_name,
        email=request.email,
        password=request.password,
        invitation_token=request.invitation_token,
    )

    return {
        "success": True,
        "user_id": user.id,
        "organization_id":
        user.organization_id,
        "role_id":
        user.role_id,
    }
