from pydantic import BaseModel


class ActivityCreate(BaseModel):
    lead_id: int
    activity_type: str
    description: str | None = None


class ActivityResponse(BaseModel):
    id: int
    lead_id: int
    activity_type: str
    description: str | None = None
    created_at: str

    model_config = {
        "from_attributes": True
    }
