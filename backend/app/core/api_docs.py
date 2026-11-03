"""Production-safe API schema exposure policy."""
import os
from typing import TypedDict, cast


class ApiDocsConfig(TypedDict):
    docs_url: str | None
    redoc_url: str | None
    openapi_url: str | None


def api_docs_config(app_env: str | None = None) -> ApiDocsConfig:
    environment = cast(str, app_env or os.getenv("APP_ENV", "production")).strip().lower()
    if environment in {"production", "prod"}:
        return {"docs_url": None, "redoc_url": None, "openapi_url": None}
    return {
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "openapi_url": "/openapi.json",
    }
