from datetime import datetime
from pydantic import BaseModel, ConfigDict


class AuditResponse(BaseModel):
    id: int
    event_type: str
    resource_type: str | None = None
    description: str | None = None
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
