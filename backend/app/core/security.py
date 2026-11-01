"""JWT issuance and verification with explicit key IDs.

The legacy SECRET_KEY variable is intentionally unsupported. Tokens without a
known kid are rejected, so the historically exposed key cannot remain a
verification fallback.
"""
import json
import os
import re
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
)
JWT_ISSUER = os.getenv("JWT_ISSUER", "syj-nexusintel-ai")
JWT_AUDIENCE = os.getenv("JWT_AUDIENCE", "syj-nexusintel-ai-client")
_KID_PATTERN = re.compile(r"^[A-Za-z0-9._-]{1,64}$")


def _load_signing_keys() -> tuple[dict[str, str], str]:
    raw_keys = os.getenv("JWT_SIGNING_KEYS", "")
    active_kid = os.getenv("JWT_ACTIVE_KID", "").strip()
    if not raw_keys or not active_kid:
        raise RuntimeError(
            "JWT_SIGNING_KEYS and JWT_ACTIVE_KID must be configured. "
            "The legacy SECRET_KEY setting is not supported."
        )
    try:
        parsed = json.loads(raw_keys)
    except json.JSONDecodeError as exc:
        raise RuntimeError("JWT_SIGNING_KEYS must be valid JSON.") from exc
    if not isinstance(parsed, dict) or not parsed:
        raise RuntimeError("JWT_SIGNING_KEYS must be a non-empty JSON object.")
    keys: dict[str, str] = {}
    for kid, secret in parsed.items():
        if not isinstance(kid, str) or not _KID_PATTERN.fullmatch(kid):
            raise RuntimeError("JWT_SIGNING_KEYS contains an invalid key ID.")
        if not isinstance(secret, str) or len(secret.encode("utf-8")) < 32:
            raise RuntimeError(
                f"JWT key '{kid}' must contain at least 32 UTF-8 bytes."
            )
        keys[kid] = secret
    if active_kid not in keys:
        raise RuntimeError("JWT_ACTIVE_KID must identify a configured signing key.")
    return keys, active_kid


JWT_SIGNING_KEYS, JWT_ACTIVE_KID = _load_signing_keys()

pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto",
)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict[str, Any]) -> str:
    now = datetime.now(timezone.utc)
    claims = data.copy()
    claims.update(
        {
            "iat": now,
            "nbf": now,
            "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
            "iss": JWT_ISSUER,
            "aud": JWT_AUDIENCE,
        }
    )
    return jwt.encode(
        claims,
        JWT_SIGNING_KEYS[JWT_ACTIVE_KID],
        algorithm=ALGORITHM,
        headers={"kid": JWT_ACTIVE_KID, "typ": "JWT"},
    )


def verify_token(token: str) -> dict[str, Any] | None:
    try:
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")
        if not isinstance(kid, str) or not _KID_PATTERN.fullmatch(kid):
            return None
        signing_key = JWT_SIGNING_KEYS.get(kid)
        if signing_key is None:
            return None
        payload = jwt.decode(
            token,
            signing_key,
            algorithms=[ALGORITHM],
            issuer=JWT_ISSUER,
            audience=JWT_AUDIENCE,
            options={"require_exp": True, "require_iat": True, "require_nbf": True},
        )
        return payload
    except (JWTError, TypeError, ValueError):
        return None
