from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.schemas.activity import (
    ActivityCreate,
    ActivityResponse,
)

from app.services.activity_service import (
    create_activity,
    get_lead_activities,
)

from app.core.dependencies import (
    get_current_user,
)

router = APIRouter(
    prefix="/activities",
    tags=["Activities"],
)


@router.post(
    "",
    response_model=ActivityResponse,
)
def create_activity_route(
    activity: ActivityCreate,
    db: Session = Depends(get_db),
    current_user=Depends(
        get_current_user
    ),
):
    return create_activity(
        db,
        activity,
        current_user["organization_id"],
    )


@router.get(
    "/{lead_id}",
    response_model=list[ActivityResponse],
)
def get_activities_route(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        get_current_user
    ),
):
    return get_lead_activities(
        db,
        lead_id,
        current_user["organization_id"],
    )
