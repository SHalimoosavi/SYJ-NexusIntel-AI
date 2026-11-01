from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.crm import OrganizationDashboardResponse

from app.core.dependencies import (
    get_current_user,
)

from app.services.organization_dashboard_service import (
    get_organization_dashboard,
)

router = APIRouter(
    prefix="/organization-dashboard",
    tags=["Organization Dashboard"],
)


@router.get("", response_model=OrganizationDashboardResponse)
def organization_dashboard(
    db: Session = Depends(get_db),
    current_user=Depends(
        get_current_user
    ),
):
    return get_organization_dashboard(
        db,
        current_user[
            "organization_id"
        ],
    )
