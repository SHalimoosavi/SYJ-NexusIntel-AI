from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class LeadNoteCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    lead_id: int = Field(gt=0)
    note: str = Field(min_length=1, max_length=10000)
    note_type: str = Field(default="GENERAL", min_length=1, max_length=40)


class LeadNoteResponse(BaseModel):
    id: int
    lead_id: int
    note: str
    note_type: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
