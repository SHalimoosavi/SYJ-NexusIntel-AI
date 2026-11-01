from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.models.user import User
from app.models.role import Role

from app.services.audit_service import (
    log_event,
)


def get_users(
    db: Session,
    organization_id: int,
):
    return (
        db.query(User)
        .filter(
            User.organization_id
            == organization_id
        )
        .order_by(
            User.id.desc()
        )
        .all()
    )


def get_user(
    db: Session,
    user_id: int,
    organization_id: int,
):
    return (
        db.query(User)
        .filter(
            User.id == user_id,
            User.organization_id
            == organization_id,
        )
        .first()
    )


def update_user_role(
    db: Session,
    user_id: int,
    role_id: int,
    organization_id: int,
    actor_user_id: int,
    actor_role_name: str = "ORGANIZATION_OWNER",
):
    user = get_user(
        db,
        user_id,
        organization_id,
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
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
            status_code=404,
            detail="Role not found",
        )

    if user.id == actor_user_id:
        raise HTTPException(status_code=400, detail="Cannot change your own role")

    if actor_role_name != "SUPER_ADMIN" and role.name not in {
        "MANAGER",
        "SALES_REPRESENTATIVE",
        "VIEWER",
    }:
        raise HTTPException(status_code=403, detail="Role assignment is not permitted")

    user.role_id = role_id

    db.commit()

    db.refresh(user)

    log_event(
        db=db,
        organization_id=organization_id,
        user_id=actor_user_id,
        event_type="USER_ROLE_UPDATED",
        resource_type="USER",
        resource_id=user.id,
        description=(
            f"Role changed for "
            f"{user.email}"
        ),
    )

    return user


def update_user_status(
    db: Session,
    user_id: int,
    is_active: bool,
    organization_id: int,
    actor_user_id: int,
):
    user = get_user(
        db,
        user_id,
        organization_id,
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    if user.id == actor_user_id:
        raise HTTPException(
            status_code=400,
            detail="Cannot deactivate yourself",
        )

    user.is_active = is_active

    db.commit()

    db.refresh(user)

    log_event(
        db=db,
        organization_id=organization_id,
        user_id=actor_user_id,
        event_type="USER_STATUS_UPDATED",
        resource_type="USER",
        resource_id=user.id,
        description=(
            f"Status changed for "
            f"{user.email}"
        ),
    )

    return user


def delete_user(
    db: Session,
    user_id: int,
    organization_id: int,
    actor_user_id: int,
):
    user = get_user(
        db,
        user_id,
        organization_id,
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    if user.id == actor_user_id:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete yourself",
        )

    db.delete(user)

    db.commit()

    log_event(
        db=db,
        organization_id=organization_id,
        user_id=actor_user_id,
        event_type="USER_DELETED",
        resource_type="USER",
        resource_id=user_id,
        description=(
            f"Deleted user "
            f"{user.email}"
        ),
    )

    return True
