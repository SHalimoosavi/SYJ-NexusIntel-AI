from pydantic import BaseModel


class SalesPitchRequest(BaseModel):
    business_name: str
    domain: str
    lead_score: int


class FollowUpRequest(BaseModel):
    business_name: str
    pipeline_stage: str
