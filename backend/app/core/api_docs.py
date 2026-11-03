"""Production-safe API schema exposure policy."""
import os


def api_docs_config(app_env: str | None = None) -> dict[str, str | None]:
    environment = (app_env if app_env is not None else os.getenv("APP_ENV") or "production").strip().lower()
    if environment in {"production", "prod"}:
        return {"docs_url": None, "redoc_url": None, "openapi_url": None}
    return {
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "openapi_url": "/openapi.json",
    }
