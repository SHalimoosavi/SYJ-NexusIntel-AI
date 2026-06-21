from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.core.security import verify_token

from app.models.user import User


security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(
        security
    ),
    db: Session = Depends(get_db),
):
    token = credentials.credentials

    payload = verify_token(token)

    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
        )

    user = (
        db.query(User)
        .filter(
            User.id == payload["user_id"]
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return user
