from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.schemas.sales_agent import SalesPitchRequest, FollowUpRequest, SalesPitchResponse, FollowUpResponse, SalesPriorityResponse

from app.services.sales_agent_service import (
    get_sales_priorities,
    generate_pitch,
    generate_followup,
)

from app.services.ai_usage_service import (
    enforce_ai_limit,
    log_ai_request,
)

from app.core.dependencies import (
    get_current_user,
)

router = APIRouter(
    prefix="/sales-agent",
    tags=["Sales Agent"],
)


@router.get("/priorities", response_model=list[SalesPriorityResponse])
def priorities(
    db: Session = Depends(get_db),
    current_user=Depends(
        get_current_user
    ),
):
    return get_sales_priorities(
        db,
        current_user[
            "organization_id"
        ],
    )


@router.post("/pitch", response_model=SalesPitchResponse)
def pitch(
    request: SalesPitchRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        get_current_user
    ),
):
    organization_id = current_user[
        "organization_id"
    ]

    enforce_ai_limit(
        db,
        organization_id,
    )

    result = generate_pitch(
        request.business_name,
        request.domain,
        request.lead_score,
    )

    log_ai_request(
        db,
        organization_id,
        "SALES_PITCH",
        current_user["user_id"],
    )

    return result


@router.post("/followup", response_model=FollowUpResponse)
def followup(
    request: FollowUpRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        get_current_user
    ),
):
    organization_id = current_user[
        "organization_id"
    ]

    enforce_ai_limit(
        db,
        organization_id,
    )

    result = generate_followup(
        request.business_name,
        request.pipeline_stage,
    )

    log_ai_request(
        db,
        organization_id,
        "SALES_FOLLOWUP",
        current_user["user_id"],
    )

    return result
