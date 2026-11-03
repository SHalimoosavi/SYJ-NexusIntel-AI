from pydantic import BaseModel, field_validator

from app.core.input_validation import validate_domain
from app.schemas.intelligence import IntelligenceResponse
from app.schemas.opportunity import OpportunityResponse
from app.schemas.sales_agent import SalesPitchResponse


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
    research_agent: IntelligenceResponse
    opportunity_agent: OpportunityResponse
    sales_agent: SalesPitchResponse
    executive_agent: ExecutiveAgentSummary
    memory_saved: bool
