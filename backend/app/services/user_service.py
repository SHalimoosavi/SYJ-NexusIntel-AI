from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.user import User
from app.services.audit_service import log_event

# A per-process dummy hash makes unknown-user and wrong-password paths perform
# the same password-hash verification work. It is not an authentication secret.
_DUMMY_PASSWORD_HASH = hash_password("syj-auth-timing-dummy-password")


def burn_password_check(password: str) -> None:
    verify_password(password, _DUMMY_PASSWORD_HASH)


def get_user_by_email(db: Session, email: str):
    normalized_email = email.strip().lower()
    return db.query(User).filter(User.email == normalized_email).first()


def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    stored_hash = user.hashed_password if user is not None else _DUMMY_PASSWORD_HASH
    password_valid = verify_password(password, stored_hash)

    if user is None or not user.is_active or not password_valid:
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
