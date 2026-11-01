from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.schemas.technology import TechnologyRequest, TechnologyResponse

from app.services.technology_service import (
    detect_technologies,
)

from app.services.ai_usage_service import (
    enforce_ai_limit,
    log_ai_request,
)

from app.core.dependencies import (
    get_current_user,
)

router = APIRouter(
    prefix="/technology",
    tags=["Technology Detection"],
)


@router.post("/detect", response_model=TechnologyResponse)
def technology_detection(
    request: TechnologyRequest,
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

    result = detect_technologies(
        request.domain
    )

    log_ai_request(
        db,
        organization_id,
        "TECHNOLOGY_DETECTION",
        current_user["user_id"],
    )

    return result
