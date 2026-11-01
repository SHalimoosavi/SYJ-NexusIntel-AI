from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.input_validation import validate_domain


class SalesPitchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    business_name: str = Field(min_length=1, max_length=160)
    domain: str
    lead_score: int = Field(ge=0, le=100)

    @field_validator("domain")
    @classmethod
    def validate_public_domain(cls, value: str) -> str:
        return validate_domain(value)


class FollowUpRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    business_name: str = Field(min_length=1, max_length=160)
    pipeline_stage: str = Field(min_length=1, max_length=32)


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
