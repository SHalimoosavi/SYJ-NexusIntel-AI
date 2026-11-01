from app.models.user import User
from app.services.user_service import authenticate_user
from app.core.security import hash_password


def test_unknown_user_and_wrong_password_return_same_authentication_result(tenant_db):
    db = tenant_db.db
    user = tenant_db.user_a
    user.hashed_password = hash_password("correct-password-123")
    db.commit()

    wrong_password = authenticate_user(
        db,
        user.email,
        "incorrect-password-123",
    )
    unknown_user = authenticate_user(
        db,
        "not-a-real-account@example.invalid",
        "incorrect-password-123",
    )

    assert wrong_password is None
    assert unknown_user is None
