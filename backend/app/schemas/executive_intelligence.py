from pydantic import BaseModel


class ExecutiveBriefingResponse(BaseModel):
    pipeline_value: int
    forecast_revenue: float
    annual_projection: float
    close_rate: float

    executive_summary: str
    risk_summary: str
    recommendation: str


class OpportunitySummaryResponse(BaseModel):
    id: int
    business_name: str
    estimated_value: int | None = None
    pipeline_stage: str | None = None


class ExecutiveRisksResponse(BaseModel):
    risk_count: int
    risks: list[str]
