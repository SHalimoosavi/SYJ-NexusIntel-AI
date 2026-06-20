from pydantic import BaseModel


class LeadQualificationRequest(BaseModel):
    domain: str
