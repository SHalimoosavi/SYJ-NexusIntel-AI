import os

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import verify_token
from app.core.rate_limit import RateLimitBackendUnavailable, rate_limit_manager
from app.database.database import get_db
from app.models.role import Role
from app.models.user import User

security = HTTPBearer(auto_error=False)
_UNSAFE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


def allowed_origins() -> set[str]:
    configured = os.getenv(
        "CORS_ORIGINS",
        "https://syj-nexus-intel-ai.vercel.app,http://localhost:3000",
    )
    return {origin.strip().rstrip("/") for origin in configured.split(",") if origin.strip()}


def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db),
):
    bearer_token = credentials.credentials if credentials else None
    cookie_token = request.cookies.get("access_token")
    token = bearer_token or cookie_token
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")

    if cookie_token and not bearer_token and request.method in _UNSAFE_METHODS:
        origin = request.headers.get("origin", "").rstrip("/")
        if not origin or origin not in allowed_origins():
            raise HTTPException(status_code=403, detail="Untrusted request origin")

    payload = verify_token(token)
    if not payload or not isinstance(payload.get("user_id"), int):
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = db.query(User).filter(User.id == payload["user_id"]).first()
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="User is inactive or unavailable")
    if user.organization_id is None or user.role_id is None:
        raise HTTPException(status_code=403, detail="User is not assigned to an organization and role")

    role = db.query(Role).filter(Role.id == user.role_id).first()
    if role is None:
        raise HTTPException(status_code=403, detail="User role is unavailable")

    try:
        user_allowed, user_retry = rate_limit_manager.check(
            f"user:{user.id}",
            300,
            60,
        )
        organization_allowed, organization_retry = rate_limit_manager.check(
            f"organization:{user.organization_id}",
            1800,
            60,
        )
    except RateLimitBackendUnavailable:
        raise HTTPException(
            status_code=503,
            detail="Rate limiting service unavailable",
            headers={"Retry-After": "5"},
        )

    if not user_allowed or not organization_allowed:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please retry later.",
            headers={"Retry-After": str(max(1, user_retry, organization_retry))},
        )

    return {
        "user_id": user.id,
        "sub": user.email,
        "organization_id": user.organization_id,
        "role_id": user.role_id,
        "role_name": role.name,
    }
