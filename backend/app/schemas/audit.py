from pydantic import BaseModel


class AuditResponse(BaseModel):
    id: int

    organization_id: int | None = None
    user_id: int | None = None

    event_type: str

    resource_type: str | None = None
    resource_id: int | None = None

    description: str | None = None

    created_at: str | None = None

    model_config = {
        "from_attributes": True
    }
