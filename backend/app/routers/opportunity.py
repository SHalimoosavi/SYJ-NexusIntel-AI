from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.schemas.opportunity import (
    OpportunityRequest,
)

from app.services.opportunity_service import (
    analyze_opportunity,
)

from app.services.ai_usage_service import (
    enforce_ai_limit,
    log_ai_request,
)

from app.core.dependencies import (
    get_current_user,
)

router = APIRouter(
    prefix="/opportunity",
    tags=["Opportunity Finder"],
)


@router.post("/analyze")
def opportunity_analysis(
    request: OpportunityRequest,
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

    result = analyze_opportunity(
        request.domain
    )

    log_ai_request(
        db,
        organization_id,
        "OPPORTUNITY_ANALYSIS",
    )

    return result
