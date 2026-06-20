from pydantic import BaseModel


class BusinessSearchRequest(BaseModel):
    city: str
    category: str
