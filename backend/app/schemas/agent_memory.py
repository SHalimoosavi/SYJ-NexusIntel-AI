from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.input_validation import validate_domain


class AgentMemoryCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    domain: str = Field(min_length=3, max_length=253)
    overall_score: int = Field(default=0, ge=0, le=100)
    priority: str = Field(default="UNKNOWN", min_length=1, max_length=32)
    estimated_value: str = Field(default="", max_length=120)
    analysis_data: dict[str, Any] = Field(default_factory=dict)

    @field_validator("domain")
    @classmethod
    def validate_public_domain(cls, value: str) -> str:
        return validate_domain(value)


class AgentMemoryResponse(BaseModel):
    id: int
    domain: str
    overall_score: int
    priority: str
    estimated_value: str | None = None
    analysis_data: str
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
