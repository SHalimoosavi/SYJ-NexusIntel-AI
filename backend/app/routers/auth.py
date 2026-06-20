from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.schemas.user import UserCreate
from app.schemas.user import UserLogin

from app.services.user_service import create_user
from app.services.user_service import get_user_by_email
from app.services.user_service import authenticate_user

from app.core.security import create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/register")
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):

    existing_user = get_user_by_email(
        db,
        user.email
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    new_user = create_user(
        db,
        user.full_name,
        user.email,
        user.password
    )

    return {
        "success": True,
        "user_id": new_user.id,
        "email": new_user.email
    }


@router.post("/login")
def login(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):

    user = authenticate_user(
        db,
        credentials.email,
        credentials.password
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    token = create_access_token(
        {
            "sub": user.email,
            "user_id": user.id
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }
