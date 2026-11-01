from sqlalchemy.orm import Session

from app.core.security import verify_password
from app.models.user import User
from app.services.audit_service import log_event


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user or not user.is_active:
        return None
    if not verify_password(password, user.hashed_password):
        return None

    log_event(
        db=db,
        organization_id=user.organization_id,
        user_id=user.id,
        event_type="USER_LOGIN",
        resource_type="USER",
        resource_id=user.id,
        description="User login succeeded",
    )
    return user
