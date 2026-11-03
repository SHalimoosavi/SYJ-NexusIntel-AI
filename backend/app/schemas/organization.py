from pydantic import BaseModel, ConfigDict, Field


class OrganizationCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str = Field(min_length=2, max_length=160)
    slug: str = Field(min_length=2, max_length=80, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class OrganizationResponse(BaseModel):
    id: int
    name: str
    slug: str
    plan: str
    max_users: int
    max_leads: int
    max_ai_requests: int

    model_config = ConfigDict(from_attributes=True)
