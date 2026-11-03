from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.core.rbac import (
    require_roles,
)

from app.schemas.audit import AuditResponse

from app.services.audit_dashboard_service import (
    get_audit_logs,
    get_event_summary,
)

router = APIRouter(
    prefix="/audit",
    tags=["Audit Dashboard"],
)


@router.get(
    "/logs",
    response_model=list[AuditResponse],
)
def audit_logs(
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
    return get_audit_logs(
        db,
        current_user["organization_id"],
    )


@router.get("/events", response_model=dict[str, int])
def audit_events(
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
    return get_event_summary(
        db,
        current_user["organization_id"],
    )
