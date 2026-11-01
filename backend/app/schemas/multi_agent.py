from pydantic import BaseModel, field_validator

from app.core.input_validation import validate_domain


class MultiAgentRequest(BaseModel):
    domain: str

    @field_validator("domain")
    @classmethod
    def validate_public_domain(cls, value: str) -> str:
        return validate_domain(value)


class ExecutiveAgentSummary(BaseModel):
    executive_summary: str
    recommendation: str


class MultiAgentResponse(BaseModel):
    research_agent: dict
    opportunity_agent: dict
    sales_agent: dict
    executive_agent: ExecutiveAgentSummary
    memory_saved: bool
