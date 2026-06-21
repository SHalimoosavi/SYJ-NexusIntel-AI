from pydantic import BaseModel


class SubscriptionCreate(BaseModel):
    organization_id: int
    plan_name: str = "FREE"


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

    model_config = {
        "from_attributes": True
    }
