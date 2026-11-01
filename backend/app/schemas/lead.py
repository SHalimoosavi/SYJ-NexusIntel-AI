from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class LeadCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    business_name: str = Field(min_length=1, max_length=200)
    contact_person: str | None = Field(default=None, max_length=120)
    email: str | None = Field(default=None, max_length=254)
    phone: str | None = Field(default=None, max_length=32)
    website: str | None = Field(default=None, max_length=253)
    city: str | None = Field(default=None, max_length=120)
    category: str | None = Field(default=None, max_length=120)
    industry: str | None = Field(default=None, max_length=120)
    company_size: str | None = Field(default=None, max_length=32)
    notes: str | None = Field(default=None, max_length=5000)
    source: str | None = Field(default=None, max_length=120)
    status: str = Field(default="NEW", min_length=1, max_length=32)
    pipeline_stage: str = Field(default="NEW", min_length=1, max_length=32)
    estimated_value: int = Field(default=0, ge=0, le=2_000_000_000)
    last_contacted: str | None = Field(default=None, max_length=40)
    next_followup: str | None = Field(default=None, max_length=40)


class LeadUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    status: str = Field(min_length=1, max_length=32)
    pipeline_stage: str = Field(min_length=1, max_length=32)
    estimated_value: int = Field(ge=0, le=2_000_000_000)
    probability: int = Field(ge=0, le=100)
    actual_revenue: int = Field(default=0, ge=0, le=2_000_000_000)
    last_contacted: str | None = Field(default=None, max_length=40)
    next_followup: str | None = Field(default=None, max_length=40)


class LeadResponse(BaseModel):
    id: int
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
    status: str
    pipeline_stage: str
    estimated_value: int
    lead_score: int
    priority: str
    probability: int
    actual_revenue: int
    last_contacted: str | None = None
    next_followup: str | None = None
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
