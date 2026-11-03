from pydantic import BaseModel, field_validator

from app.core.input_validation import validate_domain


class ReportRequest(BaseModel):
    domain: str

    @field_validator("domain")
    @classmethod
    def validate_public_domain(cls, value: str) -> str:
        return validate_domain(value)


class ReportGenerationResponse(BaseModel):
    success: bool
    report_id: str


class ReportResponse(BaseModel):
    success: bool
    report_id: str
