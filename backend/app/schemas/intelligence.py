from pydantic import BaseModel


class IntelligenceRequest(BaseModel):
    domain: str
