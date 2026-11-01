from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.schemas.report import ReportRequest, ReportGenerationResponse

from app.services.report_service import (
    generate_pdf_report,
)

from app.services.ai_usage_service import (
    enforce_ai_limit,
    log_ai_request,
)

from app.core.feature_guard import (
    require_feature,
)

from app.core.feature_constants import (
    ADVANCED_REPORTING,
)

router = APIRouter(
    prefix="/reports",
    tags=["PDF Reports"],
)


@router.post("/generate", response_model=ReportGenerationResponse)
def generate_report(
    request: ReportRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_feature(
            ADVANCED_REPORTING
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

    result = generate_pdf_report(
        request.domain
    )

    log_ai_request(
        db,
        organization_id,
        "PDF_REPORT",
        current_user["user_id"],
    )

    return result
