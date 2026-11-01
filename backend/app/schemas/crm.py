from pydantic import BaseModel

from app.schemas.revenue_forecast import RevenueForecastResponse


class CRMStatsResponse(BaseModel):
    total_leads: int
    hot_leads: int
    warm_leads: int
    cold_leads: int
    average_lead_score: int
    won_deals: int
    lost_deals: int
    close_rate: float


class CRMRevenueResponse(BaseModel):
    pipeline_value: int
    forecast_revenue: int
    won_revenue: int
    win_rate: float
    average_deal_size: int
    sales_velocity: int
    quarterly_projection: int
    annual_projection: int


class CRMPipelineResponse(BaseModel):
    new: int
    contacted: int
    meeting: int
    proposal: int
    negotiation: int
    won: int
    lost: int


class OrganizationDashboardResponse(BaseModel):
    organization: str | None = None
    plan: str | None = None
    users: int
    leads: int
    invitations: int


class ExecutiveDashboardResponse(BaseModel):
    users: int
    active_users: int
    leads: int
    invitations: int
    accepted_invitations: int
    ai_usage: int
    subscription: str | None = None
    crm: CRMStatsResponse
    forecast: RevenueForecastResponse
