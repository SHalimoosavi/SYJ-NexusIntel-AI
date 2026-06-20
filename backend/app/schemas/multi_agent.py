from pydantic import BaseModel


class MultiAgentRequest(BaseModel):
    domain: str
