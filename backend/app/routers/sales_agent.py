from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.schemas.sales_agent import (
    SalesPitchRequest,
    FollowUpRequest
)

from app.services.sales_agent_service import (
    get_sales_priorities,
    generate_pitch,
    generate_followup
)

router = APIRouter(
    prefix="/sales-agent",
    tags=["Sales Agent"]
)


@router.get("/priorities")
def priorities(
    db: Session = Depends(get_db)
):
    return get_sales_priorities(db)


@router.post("/pitch")
def pitch(
    request: SalesPitchRequest
):
    return generate_pitch(
        request.business_name,
        request.domain,
        request.lead_score
    )


@router.post("/followup")
def followup(
    request: FollowUpRequest
):
    return generate_followup(
        request.business_name,
        request.pipeline_stage
    )
