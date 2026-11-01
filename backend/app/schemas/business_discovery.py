from pydantic import BaseModel


class BusinessSearchRequest(BaseModel):
    city: str
    category: str


from app.schemas.lead import LeadResponse


class BusinessDiscoveryResponse(BaseModel):
    count: int
    results: list[LeadResponse]
