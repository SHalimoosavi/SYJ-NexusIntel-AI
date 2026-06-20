from pydantic import BaseModel


class AgentMemoryCreate(BaseModel):
    domain: str
    overall_score: int
    priority: str
    estimated_value: str
    analysis_data: str


class AgentMemoryResponse(
    AgentMemoryCreate
):
    id: int

    model_config = {
        "from_attributes": True
    }
