from pydantic import BaseModel


class TechnologyRequest(BaseModel):
    domain: str
