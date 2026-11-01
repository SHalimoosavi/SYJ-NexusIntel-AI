import json
import os
from datetime import datetime, timedelta, timezone

import pytest

os.environ.setdefault("JWT_ACTIVE_KID", "test-v1")
os.environ.setdefault("JWT_SIGNING_KEYS", json.dumps({"test-v1": "unit-test-fixture-only-2026-11-01-0123456789abcdef"}))

import jwt

from app.core import security


def test_new_tokens_include_active_kid_and_verify():
    token = security.create_access_token({"user_id": 17, "sub": "qa@example.invalid"})
    assert jwt.get_unverified_header(token)["kid"] == "test-v1"
    claims = security.verify_token(token)
    assert claims["user_id"] == 17
    assert claims["token_type"] == "access"
    assert claims["jti"]


def test_unknown_or_missing_kid_is_rejected():
    claims = {
        "user_id": 17,
        "iat": datetime.now(timezone.utc),
        "nbf": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
        "iss": security.JWT_ISSUER,
        "aud": security.JWT_AUDIENCE,
        "jti": "test-refresh-id",
        "token_type": "refresh",
        "session_version": 0,
    }
    unknown = jwt.encode(
        claims,
        "U" * 64,
        algorithm="HS256",
        headers={"kid": "retired-key"},
    )
    legacy = jwt.encode(claims, "L" * 64, algorithm="HS256")
    assert security.verify_token(unknown) is None
    assert security.verify_token(legacy) is None


def test_rotation_accepts_previous_key_only_while_configured(monkeypatch):
    previous = "P" * 64
    active = "A" * 64
    monkeypatch.setattr(
        security,
        "JWT_SIGNING_KEYS",
        {"previous-safe": previous, "active-new": active},
    )
    monkeypatch.setattr(security, "JWT_ACTIVE_KID", "active-new")
    issued = security.create_access_token({"user_id": 23})
    assert jwt.get_unverified_header(issued)["kid"] == "active-new"

    claims = {
        "user_id": 23,
        "iat": datetime.now(timezone.utc),
        "nbf": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
        "iss": security.JWT_ISSUER,
        "aud": security.JWT_AUDIENCE,
        "jti": "prior-session-id",
        "token_type": "access",
        "session_version": 0,
    }
    prior = jwt.encode(
        claims,
        previous,
        algorithm="HS256",
        headers={"kid": "previous-safe"},
    )
    assert security.verify_token(prior)["user_id"] == 23
    monkeypatch.setattr(security, "JWT_SIGNING_KEYS", {"active-new": active})
    assert security.verify_token(prior) is None


@pytest.mark.parametrize(
    "secret",
    [
        "REPLACE_WITH_AT_LEAST_32_RANDOM_BYTES",
        "change-me-" + ("Q" * 48),
        "unit-test-fixture-only-2026-11-01-0123456789abcdef",
        "password-" + ("R" * 40),
    ],
)
def test_placeholder_or_low_entropy_signing_key_fails_startup(monkeypatch, secret):
    monkeypatch.setenv(
        "JWT_SIGNING_KEYS",
        json.dumps({"candidate": secret}),
    )
    monkeypatch.setenv("JWT_ACTIVE_KID", "candidate")
    with pytest.raises(RuntimeError, match="placeholder/default|entropy"):
        security._load_signing_keys()


def test_signing_key_shorter_than_32_utf8_bytes_fails_startup(monkeypatch):
    monkeypatch.setenv("JWT_SIGNING_KEYS", json.dumps({"candidate": "S" * 31}))
    monkeypatch.setenv("JWT_ACTIVE_KID", "candidate")
    with pytest.raises(RuntimeError, match="at least 32 UTF-8 bytes"):
        security._load_signing_keys()


def test_missing_signing_key_fails_startup(monkeypatch):
    monkeypatch.delenv("JWT_SIGNING_KEYS", raising=False)
    monkeypatch.setenv("JWT_ACTIVE_KID", "candidate")
    with pytest.raises(RuntimeError, match="must be configured"):
        security._load_signing_keys()
