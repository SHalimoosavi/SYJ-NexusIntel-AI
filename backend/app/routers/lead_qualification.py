from fastapi import APIRouter

from app.schemas.lead_qualification import (
    LeadQualificationRequest
)

from app.services.lead_qualification_service import (
    qualify_lead
)

router = APIRouter(
    prefix="/lead-qualification",
    tags=["Lead Qualification"]
)


@router.post("/analyze")
def analyze_lead(
    request: LeadQualificationRequest
):

    return qualify_lead(
        request.domain
    )
