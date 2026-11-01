from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.schemas.lead_qualification import LeadQualificationRequest, LeadQualificationResponse

from app.services.lead_qualification_service import (
    qualify_lead,
)

from app.services.ai_usage_service import (
    enforce_ai_limit,
    log_ai_request,
)

from app.core.dependencies import (
    get_current_user,
)

router = APIRouter(
    prefix="/lead-qualification",
    tags=["Lead Qualification"],
)


@router.post("/analyze", response_model=LeadQualificationResponse)
def analyze_lead(
    request: LeadQualificationRequest,
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

    result = qualify_lead(
        request.domain
    )

    log_ai_request(
        db,
        organization_id,
        "LEAD_QUALIFICATION",
    )

    return result
