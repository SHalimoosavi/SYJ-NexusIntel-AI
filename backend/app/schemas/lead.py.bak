from pydantic import BaseModel


class LeadCreate(BaseModel):
    business_name: str
    contact_person: str | None = None
    email: str | None = None
    phone: str | None = None
    website: str | None = None
    city: str | None = None
    category: str | None = None
    notes: str | None = None
    source: str | None = None


class LeadResponse(LeadCreate):
    id: int

    model_config = {
        "from_attributes": True
    }
