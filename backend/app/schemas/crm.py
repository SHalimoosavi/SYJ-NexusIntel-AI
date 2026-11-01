from pydantic import BaseModel


class CRMStatsResponse(BaseModel):

    total_leads: int

    new_leads: int

    contacted_leads: int

    meeting_leads: int

    proposal_leads: int

    won_deals: int

    lost_deals: int


class CRMRevenueResponse(BaseModel):

    pipeline_value: int

    won_revenue: int

    forecast_revenue: int


class CRMPipelineResponse(BaseModel):

    new: int

    contacted: int

    meeting: int

    proposal: int

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
    forecast: dict
