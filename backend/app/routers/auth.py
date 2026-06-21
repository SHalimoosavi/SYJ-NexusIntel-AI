from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.schemas.user import (
    UserLogin,
)

from app.services.user_service import (
    authenticate_user,
)

from app.core.security import (
    create_access_token,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post("/login")
def login(
    credentials: UserLogin,
    db: Session = Depends(get_db),
):
    user = authenticate_user(
        db,
        credentials.email,
        credentials.password,
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
        )

    token = create_access_token(
        {
            "sub": user.email,
            "user_id": user.id,
            "organization_id": user.organization_id,
            "role_id": user.role_id,
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer",
    }
