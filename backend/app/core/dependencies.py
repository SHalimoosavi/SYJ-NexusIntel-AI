from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import verify_token
from app.database.database import get_db
from app.models.role import Role
from app.models.user import User

security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db),
):
    if credentials is None:
        raise HTTPException(status_code=401, detail="Authentication required")

    payload = verify_token(credentials.credentials)
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

    # Authorization context comes from current DB state, not stale JWT claims.
    return {
        "user_id": user.id,
        "sub": user.email,
        "organization_id": user.organization_id,
        "role_id": user.role_id,
        "role_name": role.name,
    }
