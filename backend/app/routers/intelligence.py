from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.schemas.intelligence import IntelligenceRequest, IntelligenceResponse

from app.services.intelligence_service import (
    generate_intelligence_report,
)

from app.services.ai_usage_service import (
    enforce_ai_limit,
    log_ai_request,
)

from app.core.dependencies import (
    get_current_user,
)

router = APIRouter(
    prefix="/intelligence",
    tags=["Intelligence"],
)


@router.post("/report", response_model=IntelligenceResponse)
def intelligence_report(
    request: IntelligenceRequest,
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

    result = generate_intelligence_report(
        request.domain
    )

    log_ai_request(
        db,
        organization_id,
        "INTELLIGENCE_REPORT",
    )

    return result
