from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AuditResponse(BaseModel):
    id: int
    organization_id: int | None = None
    user_id: int | None = None
    event_type: str
    resource_type: str | None = None
    resource_id: int | None = None
    description: str | None = None
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
