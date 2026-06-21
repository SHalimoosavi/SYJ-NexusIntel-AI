from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.core.dependencies import (
    get_current_user,
)

from app.models.role import Role


def require_roles(
    allowed_roles: list[str],
):
    def role_checker(
        current_user=Depends(
            get_current_user
        ),
        db: Session = Depends(get_db),
    ):
        role_id = current_user.get(
            "role_id"
        )

        if not role_id:
            raise HTTPException(
                status_code=403,
                detail="User role not assigned",
            )

        role = (
            db.query(Role)
            .filter(
                Role.id == role_id
            )
            .first()
        )

        if not role:
            raise HTTPException(
                status_code=403,
                detail="Role not found",
            )

        if role.name not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail="Access denied",
            )

        return current_user

    return role_checker
