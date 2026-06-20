from pydantic import BaseModel


class OpportunityRequest(BaseModel):
    domain: str


class OpportunityResponse(BaseModel):
    domain: str

    lead_score: int

    estimated_project_value: str

    priority: str

    service_opportunities: list[str]

    revenue_potential: str

    sales_pitch: str
