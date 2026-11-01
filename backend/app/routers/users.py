from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.rbac import require_roles
from app.database.database import get_db
from app.schemas.user_management import (
    UserRoleUpdate,
    UserStatusUpdate,
    UserManagementResponse,
)
from app.services.user_management_service import (
    get_users,
    get_user,
    update_user_role,
    update_user_status,
    delete_user,
)

router = APIRouter(prefix="/users", tags=["User Administration"])


@router.get("", response_model=list[UserManagementResponse])
def list_users_route(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(["SUPER_ADMIN", "ORGANIZATION_OWNER", "MANAGER"])
    ),
):
    return get_users(db, current_user["organization_id"])


@router.get("/{user_id}", response_model=UserManagementResponse)
def get_user_route(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(["SUPER_ADMIN", "ORGANIZATION_OWNER", "MANAGER"])
    ),
):
    user = get_user(db, user_id, current_user["organization_id"])
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}/role", response_model=UserManagementResponse)
def update_role_route(
    user_id: int,
    request: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(["SUPER_ADMIN", "ORGANIZATION_OWNER"])
    ),
):
    return update_user_role(
        db,
        user_id,
        request.role_id,
        current_user["organization_id"],
        current_user["user_id"],
        current_user["role_name"],
    )


@router.put("/{user_id}/status", response_model=UserManagementResponse)
def update_status_route(
    user_id: int,
    request: UserStatusUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(["SUPER_ADMIN", "ORGANIZATION_OWNER"])
    ),
):
    return update_user_status(
        db,
        user_id,
        request.is_active,
        current_user["organization_id"],
        current_user["user_id"],
    )


@router.delete("/{user_id}")
def delete_user_route(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(["SUPER_ADMIN", "ORGANIZATION_OWNER"])
    ),
):
    return {"success": delete_user(
        db,
        user_id,
        current_user["organization_id"],
        current_user["user_id"],
    )}
