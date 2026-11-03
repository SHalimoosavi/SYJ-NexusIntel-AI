"""Deterministic, isolated test defaults; never use production credentials."""
import json
import os
import secrets

os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("JWT_ACTIVE_KID", "test-v1")
os.environ.setdefault(
    "JWT_SIGNING_KEYS",
    json.dumps({"test-v1": secrets.token_urlsafe(48)}),
)
os.environ.setdefault("CORS_ORIGINS", "http://localhost:3000")
os.environ.setdefault("REDIS_URL", "")
