from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import verify_token
from app.database.database import get_db
from app.models.user import User

security = HTTPBearer(auto_error=False)
_UNSAFE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


def _allowed_origins() -> set[str]:
    import os

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

    # Cookie-authenticated unsafe requests require a trusted browser Origin.
    # Bearer-token clients are not ambient-cookie authenticated.
    if cookie_token and not bearer_token and request.method in _UNSAFE_METHODS:
        origin = request.headers.get("origin", "").rstrip("/")
        if not origin or origin not in _allowed_origins():
            raise HTTPException(status_code=403, detail="Untrusted request origin")

    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_id = payload.get("user_id")
    if not isinstance(user_id, int):
        raise HTTPException(status_code=401, detail="Invalid token subject")

    user = db.query(User).filter(User.id == user_id).first()
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="User is inactive or unavailable")
    if user.organization_id is None or user.role_id is None:
        raise HTTPException(status_code=403, detail="User is not assigned to an organization and role")

    # Authorization context comes from current DB state, not stale JWT claims.
    return {
        "user_id": user.id,
        "sub": user.email,
        "organization_id": user.organization_id,
        "role_id": user.role_id,
    }
