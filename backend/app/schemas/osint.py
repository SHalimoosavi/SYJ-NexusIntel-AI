from typing import Any

from pydantic import BaseModel, field_validator

from app.core.input_validation import validate_domain


class DomainRequest(BaseModel):
    domain: str

    @field_validator("domain")
    @classmethod
    def validate_public_domain(cls, value: str) -> str:
        return validate_domain(value)


class OSINTAnalysisResponse(BaseModel):
    domain: str
    ip: str | None = None
    whois: dict[str, Any]
    dns: list[str] | dict[str, Any]
    ssl: dict[str, Any]
    security_headers: dict[str, Any]
    seo: dict[str, Any]
