from pydantic import BaseModel


class LeadNoteCreate(BaseModel):
    lead_id: int
    note: str
    note_type: str = "GENERAL"


class LeadNoteResponse(BaseModel):
    id: int
    lead_id: int
    note: str
    note_type: str
    created_at: str

    model_config = {
        "from_attributes": True
    }
