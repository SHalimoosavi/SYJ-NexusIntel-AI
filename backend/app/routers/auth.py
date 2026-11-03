import hashlib
import os
import time

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.client_ip import resolve_client_ip
from app.core.rate_limit import RateLimitBackendUnavailable, rate_limit_manager
from app.core.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
    verify_token,
)
from app.database.database import get_db
from app.models.user import User
from app.schemas.user import UserLogin, PasswordChangeRequest
from app.schemas.common import AuthSessionResponse, SuccessResponse, PasswordChangedResponse
from app.services.user_service import authenticate_user, burn_password_check
from app.services.audit_service import log_event

router = APIRouter(prefix="/auth", tags=["Authentication"])
_LOGIN_FAILURE_THRESHOLD = 5
_LOGIN_LOCKOUT_SECONDS = 900
_REFRESH_TOKEN_TTL_SECONDS = REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60


def _configured_origins() -> set[str]:
    configured = {
        value.strip().rstrip("/")
        for value in os.getenv("CORS_ORIGINS", "").split(",")
        if value.strip()
    }
    if not configured and os.getenv("APP_ENV", "production").lower() in {
        "development", "dev", "local", "desktop", "test"
    }:
        return {"http://localhost:3000"}
    return configured


def _require_trusted_origin(request: Request) -> None:
    origin = request.headers.get("origin", "").rstrip("/")
    if not origin or origin not in _configured_origins():
        raise HTTPException(status_code=403, detail="Untrusted request origin")


def _login_attempt_key(client_ip: str, email: str) -> str:
    normalized = email.strip().lower()
    digest = hashlib.sha256(f"{client_ip}:{normalized}".encode("utf-8")).hexdigest()
    return f"login-attempt:{digest}"


def _account_attempt_key(email: str) -> str:
    digest = hashlib.sha256(email.strip().lower().encode("utf-8")).hexdigest()
    return f"account-login-attempt:{digest}"


def _invalid_credentials() -> HTTPException:
    return HTTPException(status_code=401, detail="Invalid credentials")


def _cookie_options(max_age: int) -> dict:
    secure_cookie = os.getenv("COOKIE_SECURE", "true").lower() == "true"
    same_site = os.getenv("COOKIE_SAMESITE", "none").lower()
    if same_site not in {"lax", "strict", "none"} or (same_site == "none" and not secure_cookie):
        raise HTTPException(status_code=500, detail="Invalid session cookie security configuration")
    return {
        "max_age": max_age,
        "httponly": True,
        "secure": secure_cookie,
        "samesite": same_site,
        "path": "/",
    }


def _delete_session_cookies(response: Response) -> None:
    options = _cookie_options(0)
    options.pop("max_age", None)
    response.delete_cookie(key="access_token", **options)
    response.delete_cookie(key="refresh_token", **options)


def _create_session_tokens(user: User, session_version: int) -> dict[str, str]:
    claims = {
        "sub": user.email,
        "user_id": user.id,
        "session_version": session_version,
    }
    return {
        "access_token": create_access_token(claims),
        "refresh_token": create_refresh_token(claims),
    }


def _set_session_cookies(response: Response, tokens: dict[str, str]) -> None:
    response.set_cookie(
        key="access_token",
        value=tokens["access_token"],
        **_cookie_options(ACCESS_TOKEN_EXPIRE_MINUTES * 60),
    )
    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        **_cookie_options(_REFRESH_TOKEN_TTL_SECONDS),
    )


def _issue_session(response: Response, user: User, session_version: int) -> None:
    _set_session_cookies(response, _create_session_tokens(user, session_version))


@router.post("/login", response_model=AuthSessionResponse)
def login(
    credentials: UserLogin,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    _require_trusted_origin(request)
    client_ip = resolve_client_ip(
        request.client.host if request.client else None,
        request.headers.get("x-forwarded-for"),
    )
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
            time.sleep(min(0.25 * (2 ** min(failures - 1, 3)), 2.0))
            raise _invalid_credentials()

        if user.organization_id is None or user.role_id is None:
            raise _invalid_credentials()

        rate_limit_manager.clear_login_failures(attempt_key)
        rate_limit_manager.clear_login_failures(account_key)
        session_version = rate_limit_manager.get_user_session_version(user.id)
        _issue_session(response, user, session_version)
    except RateLimitBackendUnavailable:
        raise HTTPException(
            status_code=503,
            detail="Authentication protection temporarily unavailable",
            headers={"Retry-After": "5"},
        )

    return {"success": True, "token_type": "cookie"}


@router.post("/refresh", response_model=AuthSessionResponse)
def refresh_session(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    _require_trusted_origin(request)
    raw_token = request.cookies.get("refresh_token")
    if not raw_token:
        raise HTTPException(status_code=401, detail="Refresh session unavailable")

    payload = verify_token(raw_token)
    if not payload or payload.get("token_type") != "refresh":
        raise HTTPException(status_code=401, detail="Refresh session unavailable")

    user_id = payload.get("user_id")
    jti = payload.get("jti")
    if not isinstance(user_id, int) or not isinstance(jti, str):
        raise HTTPException(status_code=401, detail="Refresh session unavailable")

    user = db.query(User).filter(User.id == user_id).first()
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="Refresh session unavailable")

    try:
        current_version = rate_limit_manager.get_user_session_version(user.id)
        if payload.get("session_version") != current_version:
            raise HTTPException(status_code=401, detail="Refresh session expired")

        rotation_state = rate_limit_manager.begin_refresh_rotation(
            jti,
            _REFRESH_TOKEN_TTL_SECONDS,
        )
        if rotation_state == 0:
            # A replay after the short concurrent-request grace period is treated
            # as theft and revokes the complete user session family.
            rate_limit_manager.revoke_user_sessions(user.id)
            log_event(
                db,
                user.organization_id,
                user.id,
                "REFRESH_TOKEN_REUSE",
                "USER_SESSION",
                user.id,
                "Refresh token reuse detected; sessions revoked",
            )
            raise HTTPException(status_code=401, detail="Refresh session reuse detected")

        if rotation_state == 2:
            # A parallel request waits for the first request to publish the exact
            # replacement cookie pair. It never creates a second session.
            tokens = None
            for _ in range(20):
                tokens = rate_limit_manager.get_refresh_rotation_result(jti)
                if tokens:
                    break
                time.sleep(0.05)
            if not tokens:
                raise HTTPException(
                    status_code=503,
                    detail="Session refresh is still processing; retry shortly",
                    headers={"Retry-After": "1"},
                )
        else:
            tokens = _create_session_tokens(user, current_version)
            # Logout/password-change may race a refresh. Never publish tokens for
            # a session version that has already been revoked.
            if rate_limit_manager.get_user_session_version(user.id) != current_version:
                raise HTTPException(status_code=401, detail="Refresh session expired")
            rate_limit_manager.complete_refresh_rotation(jti, tokens)

        if tokens is None:
            raise HTTPException(status_code=503, detail="Session refresh result unavailable")
        _set_session_cookies(response, tokens)
    except RateLimitBackendUnavailable:
        raise HTTPException(
            status_code=503,
            detail="Session service temporarily unavailable",
            headers={"Retry-After": "5"},
        )
    return {"success": True, "token_type": "cookie"}


@router.post("/logout", response_model=SuccessResponse)
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    if request.cookies.get("access_token") or request.cookies.get("refresh_token"):
        _require_trusted_origin(request)

    access_payload = verify_token(request.cookies.get("access_token", ""))
    refresh_payload = verify_token(request.cookies.get("refresh_token", ""))
    payload = access_payload or refresh_payload
    user_id = payload.get("user_id") if payload else None
    if isinstance(user_id, int):
        try:
            rate_limit_manager.revoke_user_sessions(user_id)
        except RateLimitBackendUnavailable:
            raise HTTPException(
                status_code=503,
                detail="Session service temporarily unavailable",
                headers={"Retry-After": "5"},
            )
        user = db.query(User).filter(User.id == user_id).first()
        if user is not None:
            log_event(
                db=db,
                organization_id=user.organization_id,
                user_id=user.id,
                event_type="USER_LOGOUT",
                resource_type="USER",
                resource_id=user.id,
                description="User logged out",
            )

    _delete_session_cookies(response)
    return {"success": True}


@router.post("/change-password", response_model=PasswordChangedResponse)
def change_password(
    request: PasswordChangeRequest,
    response: Response,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == current_user["user_id"]).first()
    if user is None or not verify_password(request.current_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    if request.current_password == request.new_password:
        raise HTTPException(status_code=400, detail="New password must be different")

    user.hashed_password = hash_password(request.new_password)

    try:
        # Revoke existing tokens before committing the new password. If Redis
        # is unavailable, the password update is not committed.
        rate_limit_manager.revoke_user_sessions(user.id)
    except RateLimitBackendUnavailable:
        raise HTTPException(
            status_code=503,
            detail="Session service temporarily unavailable",
            headers={"Retry-After": "5"},
        )

    db.commit()
    log_event(
        db=db,
        organization_id=user.organization_id,
        user_id=user.id,
        event_type="USER_PASSWORD_CHANGED",
        resource_type="USER",
        resource_id=user.id,
        description="User password changed",
    )
    _delete_session_cookies(response)
    return {"success": True, "message": "Password changed. Sign in again."}
