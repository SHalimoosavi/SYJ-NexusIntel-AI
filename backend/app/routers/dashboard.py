from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.core.dependencies import (
    get_current_user,
)

from app.services.executive_dashboard_service import (
    get_executive_dashboard,
)

router = APIRouter(
    prefix="/dashboard",
    tags=["Executive Dashboard"],
)


@router.get("/executive")
def executive_dashboard(
    db: Session = Depends(get_db),
    current_user=Depends(
        get_current_user
    ),
):
    return get_executive_dashboard(
        db,
        current_user[
            "organization_id"
        ],
    )
