from fastapi import APIRouter

from app.schemas.report import (
    ReportRequest
)

from app.services.report_service import (
    generate_pdf_report
)

router = APIRouter(
    prefix="/reports",
    tags=["PDF Reports"]
)


@router.post("/generate")
def generate_report(
    request: ReportRequest
):

    return generate_pdf_report(
        request.domain
    )
