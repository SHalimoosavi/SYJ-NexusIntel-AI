from pydantic import BaseModel, field_validator

from app.core.input_validation import validate_domain


class IntelligenceRequest(BaseModel):
    domain: str

    @field_validator("domain")
    @classmethod
    def validate_public_domain(cls, value: str) -> str:
        return validate_domain(value)


class IntelligenceResponse(BaseModel):
    domain: str
    overall_score: int
    security_score: int
    seo_score: int
    trust_score: int
    recommendations: list[str]
