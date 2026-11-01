from pydantic import BaseModel, ConfigDict, Field


class ActivityCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    lead_id: int = Field(gt=0)
    activity_type: str = Field(min_length=1, max_length=40)
    description: str | None = Field(default=None, max_length=2000)


class ActivityResponse(BaseModel):
    id: int
    lead_id: int
    activity_type: str
    description: str | None = None
    created_at: str

    model_config = ConfigDict(from_attributes=True)
