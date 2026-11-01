import os

from jose import jwt

from app.core.rate_limit import RateLimitManager
from app.core.security import ALGORITHM, JWT_ACTIVE_KID, JWT_SIGNING_KEYS, create_access_token, create_refresh_token, verify_token


def test_issued_tokens_use_active_kid_and_pinned_algorithm():
    access = create_access_token({"sub": "qa@example.invalid", "user_id": 101})
    header = jwt.get_unverified_header(access)
    payload = verify_token(access)
    assert header["kid"] == JWT_ACTIVE_KID
    assert header["alg"] == ALGORITHM == "HS256"
    assert payload is not None and payload["token_type"] == "access"


def test_refresh_token_is_typed_and_rotation_jti_is_single_use():
    refresh = create_refresh_token({"sub": "qa@example.invalid", "user_id": 101})
    payload = verify_token(refresh)
    assert payload is not None and payload["token_type"] == "refresh"
    manager = RateLimitManager(redis_url="", app_env="test")
    assert manager.consume_refresh_jti(payload["jti"], 300)
    assert not manager.consume_refresh_jti(payload["jti"], 300)


def test_user_session_revocation_invalidates_prior_session_version():
    manager = RateLimitManager(redis_url="", app_env="test")
    original_version = manager.get_user_session_version(101)
    assert original_version == 0
    assert manager.revoke_user_sessions(101) == 1
    assert manager.get_user_session_version(101) != original_version


def test_token_with_unknown_kid_or_wrong_algorithm_is_rejected():
    claims = {
        "sub": "qa@example.invalid",
        "user_id": 101,
        "iat": 1_800_000_000,
        "nbf": 1_800_000_000,
        "exp": 1_800_000_600,
        "iss": os.getenv("JWT_ISSUER", "syj-nexusintel-ai"),
        "aud": os.getenv("JWT_AUDIENCE", "syj-nexusintel-ai-client"),
        "jti": "unknown-kid-test",
        "token_type": "access",
        "session_version": 0,
    }
    unknown_kid = jwt.encode(
        claims,
        JWT_SIGNING_KEYS[JWT_ACTIVE_KID],
        algorithm=ALGORITHM,
        headers={"kid": "not-configured"},
    )
    assert verify_token(unknown_kid) is None
    wrong_algorithm = jwt.encode(
        claims,
        JWT_SIGNING_KEYS[JWT_ACTIVE_KID],
        algorithm="HS384",
        headers={"kid": JWT_ACTIVE_KID},
    )
    assert verify_token(wrong_algorithm) is None
