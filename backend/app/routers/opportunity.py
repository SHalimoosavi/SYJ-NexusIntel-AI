from fastapi import APIRouter

from app.schemas.opportunity import (
    OpportunityRequest
)

from app.services.opportunity_service import (
    analyze_opportunity
)

router = APIRouter(
    prefix="/opportunity",
    tags=["Opportunity Finder"]
)


@router.post("/analyze")
def opportunity_analysis(
    request: OpportunityRequest
):

    return analyze_opportunity(
        request.domain
    )
