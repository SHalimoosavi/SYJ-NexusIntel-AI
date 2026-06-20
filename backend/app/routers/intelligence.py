from fastapi import APIRouter

from app.schemas.intelligence import (
    IntelligenceRequest
)

from app.services.intelligence_service import (
    generate_intelligence_report
)

router = APIRouter(
    prefix="/intelligence",
    tags=["Intelligence"]
)


@router.post("/report")
def intelligence_report(
    request: IntelligenceRequest
):

    return generate_intelligence_report(
        request.domain
    )
