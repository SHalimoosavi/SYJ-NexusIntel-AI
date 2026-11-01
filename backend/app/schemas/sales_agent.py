from pydantic import BaseModel, field_validator

from app.core.input_validation import validate_domain


class SalesPitchRequest(BaseModel):
    business_name: str
    domain: str
    lead_score: int

    @field_validator("domain")
    @classmethod
    def validate_public_domain(cls, value: str) -> str:
        return validate_domain(value)


class FollowUpRequest(BaseModel):
    business_name: str
    pipeline_stage: str
