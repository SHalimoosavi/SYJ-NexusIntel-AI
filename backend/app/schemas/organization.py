from pydantic import BaseModel


class OrganizationCreate(BaseModel):
    name: str
    slug: str


class OrganizationResponse(BaseModel):
    id: int
    name: str
    slug: str

    plan: str

    max_users: int
    max_leads: int
    max_ai_requests: int

    model_config = {
        "from_attributes": True
    }
