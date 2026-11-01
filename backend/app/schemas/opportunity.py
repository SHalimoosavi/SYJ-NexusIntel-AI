from pydantic import BaseModel, field_validator

from app.core.input_validation import validate_domain


class OpportunityRequest(BaseModel):
    domain: str


    @field_validator("domain")
    @classmethod
    def validate_public_domain(cls, value: str) -> str:
        return validate_domain(value)


class OpportunityResponse(BaseModel):
    domain: str

    lead_score: int

    estimated_project_value: str

    priority: str

    service_opportunities: list[str]

    revenue_potential: str

    sales_pitch: str
