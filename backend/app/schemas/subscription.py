from pydantic import BaseModel, ConfigDict, Field


class SubscriptionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    organization_id: int = Field(gt=0)
    plan_name: str = Field(default="FREE", min_length=1, max_length=40)


class SubscriptionResponse(BaseModel):
    id: int
    organization_id: int
    plan_name: str
    max_users: int
    max_leads: int
    max_ai_requests: int
    max_whatsapp_campaigns: int
    max_email_campaigns: int
    status: str

    model_config = ConfigDict(from_attributes=True)
