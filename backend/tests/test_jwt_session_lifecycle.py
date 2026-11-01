import json
import os

import pytest
from jose import jwt

os.environ.setdefault("JWT_ACTIVE_KID", "test-v1")
os.environ.setdefault("JWT_SIGNING_KEYS", json.dumps({"test-v1": "T" * 64}))

from app.core import security
from app.core.rate_limit import RateLimitManager


def test_access_token_is_typed_short_lived_and_verifiable():
    token = security.create_access_token(
        {"sub": "qa@example.invalid", "user_id": 12, "session_version": 0}
    )
    payload = security.verify_token(token)
    assert payload is not None
    assert payload["token_type"] == "access"
    assert payload["user_id"] == 12
    assert payload["session_version"] == 0
    assert payload["exp"] - payload["iat"] <= security.ACCESS_TOKEN_EXPIRE_MINUTES * 60


def test_token_tampering_is_rejected():
    token = security.create_access_token({"sub": "qa@example.invalid", "user_id": 12})
    tampered = token[:-1] + ("A" if token[-1] != "A" else "B")
    assert security.verify_token(tampered) is None


def test_unknown_kid_and_unapproved_algorithm_are_rejected():
    payload = {
        "sub": "qa@example.invalid",
        "user_id": 12,
        "token_type": "access",
        "session_version": 0,
    }
    unknown_kid = jwt.encode(
        payload,
        "T" * 64,
        algorithm="HS256",
        headers={"kid": "unknown-v9"},
    )
    wrong_algorithm = jwt.encode(
        payload,
        "T" * 64,
        algorithm="HS384",
        headers={"kid": "test-v1"},
    )
    assert security.verify_token(unknown_kid) is None
    assert security.verify_token(wrong_algorithm) is None


def test_refresh_jti_is_single_use_and_session_version_revokes_tokens():
    manager = RateLimitManager(redis_url="", app_env="test")
    assert manager.consume_refresh_jti("refresh-jti", 300)
    assert not manager.consume_refresh_jti("refresh-jti", 300)
    assert manager.get_user_session_version(44) == 0
    assert manager.revoke_user_sessions(44) == 1
    assert manager.get_user_session_version(44) == 1
