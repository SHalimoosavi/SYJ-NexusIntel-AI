from fastapi import Depends
from fastapi import HTTPException

from fastapi.security import (
    HTTPBearer,
)

from fastapi.security import (
    HTTPAuthorizationCredentials,
)

from app.core.security import (
    verify_token,
)

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(
        security
    ),
):
    token = credentials.credentials

    payload = verify_token(token)

    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
        )

    required_fields = [
        "user_id",
        "organization_id",
        "role_id",
    ]

    for field in required_fields:

        if field not in payload:
            raise HTTPException(
                status_code=401,
                detail=(
                    f"Missing token field: "
                    f"{field}"
                ),
            )

    return payload
