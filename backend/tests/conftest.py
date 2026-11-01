"""Deterministic, isolated test defaults; never use production credentials."""
import json
import os

os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("JWT_ACTIVE_KID", "test-v1")
os.environ.setdefault(
    "JWT_SIGNING_KEYS",
    json.dumps({"test-v1": "unit-test-fixture-only-2026-11-01-0123456789abcdef"}),
)
os.environ.setdefault("CORS_ORIGINS", "http://localhost:3000")
os.environ.setdefault("REDIS_URL", "")
