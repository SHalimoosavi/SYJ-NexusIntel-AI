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
