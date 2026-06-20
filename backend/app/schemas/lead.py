from pydantic import BaseModel


class LeadCreate(BaseModel):
    business_name: str

    contact_person: str | None = None
    email: str | None = None
    phone: str | None = None
    website: str | None = None

    city: str | None = None
    category: str | None = None

    industry: str | None = None
    company_size: str | None = None

    notes: str | None = None
    source: str | None = None

    status: str = "NEW"
    pipeline_stage: str = "NEW"

    estimated_value: int = 0

    last_contacted: str | None = None
    next_followup: str | None = None


class LeadUpdate(BaseModel):
    status: str
    pipeline_stage: str

    estimated_value: int

    probability: int

    actual_revenue: int = 0

    last_contacted: str | None = None
    next_followup: str | None = None


class LeadResponse(LeadCreate):
    id: int

    lead_score: int
    priority: str

    probability: int
    actual_revenue: int

    model_config = {
        "from_attributes": True
    }
