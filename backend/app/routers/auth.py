import os

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.database.database import get_db
from app.schemas.user import UserLogin
from app.services.user_service import authenticate_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login")
def login(
    credentials: UserLogin,
    response: Response,
    db: Session = Depends(get_db),
):
    user = authenticate_user(db, credentials.email, credentials.password)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if user.organization_id is None or user.role_id is None:
        raise HTTPException(status_code=403, detail="User is not assigned to an organization and role")

    session_jwt = create_access_token({"sub": user.email, "user_id": user.id})
    secure_cookie = os.getenv("COOKIE_SECURE", "true").lower() == "true"
    same_site = os.getenv("COOKIE_SAMESITE", "none").lower()
    if same_site not in {"lax", "strict", "none"} or (same_site == "none" and not secure_cookie):
        raise HTTPException(status_code=500, detail="Invalid session cookie security configuration")

    response.set_cookie(
        key="access_token",
        value=session_jwt,
        max_age=3600,
        httponly=True,
        secure=secure_cookie,
        samesite=same_site,
        path="/",
    )
    return {"success": True, "token_type": "cookie"}


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(
        key="access_token",
        path="/",
        httponly=True,
        secure=os.getenv("COOKIE_SECURE", "true").lower() == "true",
        samesite=os.getenv("COOKIE_SAMESITE", "none").lower(),
    )
    return {"success": True}
