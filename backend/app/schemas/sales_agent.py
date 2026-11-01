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


class SalesPriorityResponse(BaseModel):
    id: int
    business_name: str
    estimated_value: int
    pipeline_stage: str
    score: int
    priority: str
    next_followup: str | None = None


class SalesPitchResponse(BaseModel):
    business_name: str
    priority: str
    sales_pitch: str


class FollowUpResponse(BaseModel):
    business_name: str
    pipeline_stage: str
    recommended_action: str
