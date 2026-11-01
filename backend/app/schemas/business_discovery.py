from pydantic import BaseModel, ConfigDict, Field

from app.schemas.lead import LeadResponse


class BusinessSearchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    city: str = Field(min_length=1, max_length=100)
    category: str = Field(min_length=1, max_length=100)


class BusinessDiscoveryResponse(BaseModel):
    count: int
    results: list[LeadResponse]
