import hashlib
import os
import time

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session

from app.core.rate_limit import RateLimitBackendUnavailable, rate_limit_manager
from app.core.security import create_access_token
from app.database.database import get_db
from app.schemas.user import UserLogin
from app.services.user_service import authenticate_user, burn_password_check

router = APIRouter(prefix="/auth", tags=["Authentication"])
_LOGIN_FAILURE_THRESHOLD = 5
_LOGIN_LOCKOUT_SECONDS = 900


def _login_attempt_key(client_ip: str, email: str) -> str:
    # Email is hashed before it becomes a Redis key or application log value.
    normalized = email.strip().lower()
    digest = hashlib.sha256(f"{client_ip}:{normalized}".encode("utf-8")).hexdigest()
    return f"login-attempt:{digest}"


def _account_attempt_key(email: str) -> str:
    normalized = email.strip().lower()
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    return f"account-login-attempt:{digest}"


def _invalid_credentials() -> HTTPException:
    return HTTPException(status_code=401, detail="Invalid credentials")


@router.post("/login")
def login(
    credentials: UserLogin,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    origin = request.headers.get("origin")
    configured_origins = {
        value.strip().rstrip("/")
        for value in os.getenv("CORS_ORIGINS", "").split(",")
        if value.strip()
    }
    if origin and origin.rstrip("/") not in configured_origins:
        raise HTTPException(status_code=403, detail="Untrusted request origin")

    client_ip = request.client.host if request.client else "unknown"
    attempt_key = _login_attempt_key(client_ip, credentials.email)
    account_key = _account_attempt_key(credentials.email)

    try:
        if rate_limit_manager.is_login_locked(attempt_key) or rate_limit_manager.is_login_locked(account_key):
            burn_password_check(credentials.password)
            time.sleep(0.5)
            raise _invalid_credentials()

        user = authenticate_user(db, credentials.email, credentials.password)
        if user is None:
            failures = rate_limit_manager.record_login_failure(
                attempt_key,
                threshold=_LOGIN_FAILURE_THRESHOLD,
                lockout_seconds=_LOGIN_LOCKOUT_SECONDS,
            )
            rate_limit_manager.record_login_failure(
                account_key,
                threshold=10,
                lockout_seconds=_LOGIN_LOCKOUT_SECONDS,
            )
            # Progressive delay is capped to avoid tying up workers indefinitely.
            time.sleep(min(0.25 * (2 ** min(failures - 1, 3)), 2.0))
            raise _invalid_credentials()

        if user.organization_id is None or user.role_id is None:
            raise _invalid_credentials()

        rate_limit_manager.clear_login_failures(attempt_key)
        rate_limit_manager.clear_login_failures(account_key)
    except RateLimitBackendUnavailable:
        raise HTTPException(
            status_code=503,
            detail="Authentication protection temporarily unavailable",
            headers={"Retry-After": "5"},
        )

    session_jwt = create_access_token({"sub": user.email, "user_id": user.id})
    secure_cookie = os.getenv("COOKIE_SECURE", "true").lower() == "true"
    same_site = os.getenv("COOKIE_SAMESITE", "none").lower()
    if same_site not in {"lax", "strict", "none"} or (same_site == "none" and not secure_cookie):
        raise HTTPException(status_code=500, detail="Invalid session cookie security configuration")

    response.set_cookie(
        key="access_token",
        value=session_jwt,
        max_age=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")) * 60,
        httponly=True,
        secure=secure_cookie,
        samesite=same_site,
        path="/",
    )
    return {"success": True, "token_type": "cookie"}


@router.post("/logout")
def logout(request: Request, response: Response):
    if request.cookies.get("access_token"):
        origin = request.headers.get("origin", "").rstrip("/")
        allowed = {
            value.strip().rstrip("/")
            for value in os.getenv("CORS_ORIGINS", "").split(",")
            if value.strip()
        }
        if not origin or origin not in allowed:
            raise HTTPException(status_code=403, detail="Untrusted request origin")
    response.delete_cookie(
        key="access_token",
        path="/",
        httponly=True,
        secure=os.getenv("COOKIE_SECURE", "true").lower() == "true",
        samesite=os.getenv("COOKIE_SAMESITE", "none").lower(),
    )
    return {"success": True}
