from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.rbac import require_roles
from app.database.database import get_db
from app.schemas.organization import OrganizationCreate, OrganizationResponse
from app.services.organization_service import (
    create_organization,
    get_organization,
    get_organizations,
)

router = APIRouter(prefix="/organizations", tags=["Organizations"])


@router.post("", response_model=OrganizationResponse)
def create_organization_route(
    organization: OrganizationCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["SUPER_ADMIN"])),
):
    return create_organization(db, organization)


@router.get("", response_model=list[OrganizationResponse])
def get_organizations_route(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(["SUPER_ADMIN", "ORGANIZATION_OWNER", "MANAGER"])
    ),
):
    if current_user["role_name"] == "SUPER_ADMIN":
        return get_organizations(db)
    return get_organizations(db, current_user["organization_id"])


@router.get("/{organization_id}", response_model=OrganizationResponse)
def get_organization_route(
    organization_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(["SUPER_ADMIN", "ORGANIZATION_OWNER", "MANAGER", "VIEWER"])
    ),
):
    tenant_id = (
        None
        if current_user["role_name"] == "SUPER_ADMIN"
        else current_user["organization_id"]
    )
    organization = get_organization(db, organization_id, tenant_id)
    if organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    return organization
