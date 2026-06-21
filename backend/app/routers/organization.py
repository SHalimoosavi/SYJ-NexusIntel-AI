from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.schemas.organization import (
    OrganizationCreate,
    OrganizationResponse,
)

from app.services.organization_service import (
    create_organization,
    get_organizations,
    get_organization,
)

from app.core.rbac import require_roles


router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"],
)


@router.post(
    "",
    response_model=OrganizationResponse,
)
def create_organization_route(
    organization: OrganizationCreate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            [
                "SUPER_ADMIN",
                "ORGANIZATION_OWNER",
            ]
        )
    ),
):
    return create_organization(
        db,
        organization,
    )


@router.get(
    "",
    response_model=list[OrganizationResponse],
)
def get_organizations_route(
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
    return get_organizations(db)


@router.get(
    "/{organization_id}",
    response_model=OrganizationResponse,
)
def get_organization_route(
    organization_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            [
                "SUPER_ADMIN",
                "ORGANIZATION_OWNER",
                "MANAGER",
                "VIEWER",
            ]
        )
    ),
):
    return get_organization(
        db,
        organization_id,
    )
