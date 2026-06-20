from pydantic import BaseModel


class ReportRequest(BaseModel):
    domain: str
