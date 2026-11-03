from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.executive_intelligence import ExecutiveBriefingResponse, OpportunitySummaryResponse, ExecutiveRisksResponse

from app.core.feature_guard import (
    require_feature,
)

from app.core.feature_constants import (
    EXECUTIVE_INTELLIGENCE,
)

from app.services.ai_usage_service import (
    enforce_ai_limit,
    log_ai_request,
)

from app.services.executive_intelligence_service import (
    generate_executive_briefing,
    get_top_opportunities,
    get_risks,
)

router = APIRouter(
    prefix="/executive-intelligence",
    tags=["Executive Intelligence"],
)


@router.get("/briefing", response_model=ExecutiveBriefingResponse)
def executive_briefing(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_feature(
            EXECUTIVE_INTELLIGENCE
        )
    ),
):
    organization_id = current_user[
        "organization_id"
    ]

    enforce_ai_limit(
        db,
        organization_id,
    )

    result = generate_executive_briefing(
        db,
        organization_id,
    )

    log_ai_request(
        db,
        organization_id,
        "EXECUTIVE_BRIEFING",
        current_user["user_id"],
    )

    return result


@router.get("/opportunities", response_model=list[OpportunitySummaryResponse])
def opportunities(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_feature(
            EXECUTIVE_INTELLIGENCE
        )
    ),
):
    organization_id = current_user[
        "organization_id"
    ]

    enforce_ai_limit(
        db,
        organization_id,
    )

    result = get_top_opportunities(
        db,
        organization_id,
    )

    log_ai_request(
        db,
        organization_id,
        "EXECUTIVE_OPPORTUNITIES",
        current_user["user_id"],
    )

    return result


@router.get("/risks", response_model=ExecutiveRisksResponse)
def risks(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_feature(
            EXECUTIVE_INTELLIGENCE
        )
    ),
):
    organization_id = current_user[
        "organization_id"
    ]

    enforce_ai_limit(
        db,
        organization_id,
    )

    result = get_risks(
        db,
        organization_id,
    )

    log_ai_request(
        db,
        organization_id,
        "EXECUTIVE_RISKS",
        current_user["user_id"],
    )

    return result
