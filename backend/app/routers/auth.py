from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.database.database import get_db
from app.schemas.user import UserLogin
from app.services.user_service import authenticate_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login")
def login(
    credentials: UserLogin,
    db: Session = Depends(get_db),
):
    user = authenticate_user(db, credentials.email, credentials.password)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if user.organization_id is None or user.role_id is None:
        raise HTTPException(status_code=403, detail="User is not assigned to an organization and role")

    token = create_access_token(
        {
            "sub": user.email,
            "user_id": user.id,
        }
    )
    # This endpoint is consumed server-to-server by the Next.js BFF.
    # The BFF stores the token in an HttpOnly, same-site browser cookie and
    # never forwards this response field to browser JavaScript.
    return {"access_token": token, "token_type": "bearer"}
