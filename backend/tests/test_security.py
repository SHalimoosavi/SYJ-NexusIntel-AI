import json
import os
from datetime import datetime, timedelta, timezone

os.environ.setdefault("JWT_ACTIVE_KID", "test-v1")
os.environ.setdefault("JWT_SIGNING_KEYS", json.dumps({"test-v1": "T" * 64}))

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
