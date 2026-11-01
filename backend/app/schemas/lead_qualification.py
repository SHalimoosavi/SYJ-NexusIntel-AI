from pydantic import BaseModel, field_validator

from app.core.input_validation import validate_domain


class LeadQualificationRequest(BaseModel):
    domain: str

    @field_validator("domain")
    @classmethod
    def validate_public_domain(cls, value: str) -> str:
        return validate_domain(value)


class LeadQualificationResponse(BaseModel):
    domain: str
    lead_score: int
    priority: str
    technologies: list[str]
    recommendations: list[str]
    sales_recommendation: str
