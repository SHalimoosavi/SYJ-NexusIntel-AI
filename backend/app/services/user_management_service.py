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
        raise HTTPException(status_code=404, detail="User not found")

    current_target_role = db.query(Role).filter(Role.id == user.role_id).first()
    if actor_role_name != "SUPER_ADMIN" and current_target_role and current_target_role.name == "SUPER_ADMIN":
        raise HTTPException(status_code=403, detail="Target user role cannot be modified")

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
            "User role updated"
        ),
    )

    return user


def _is_last_active_super_admin(db: Session, user: User) -> bool:
    role = db.query(Role).filter(Role.id == user.role_id).first()
    if role is None or role.name != "SUPER_ADMIN" or not user.is_active:
        return False
    active_count = (
        db.query(User)
        .join(Role, User.role_id == Role.id)
        .filter(Role.name == "SUPER_ADMIN", User.is_active.is_(True))
        .count()
    )
    return active_count <= 1


def update_user_status(
    db: Session,
    user_id: int,
    is_active: bool,
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
        raise HTTPException(status_code=404, detail="User not found")

    target_role = db.query(Role).filter(Role.id == user.role_id).first()
    if actor_role_name != "SUPER_ADMIN" and target_role and target_role.name in {"SUPER_ADMIN", "ORGANIZATION_OWNER"}:
        raise HTTPException(status_code=403, detail="Target user status cannot be changed")

    if user.id == actor_user_id:
        raise HTTPException(
            status_code=400,
            detail="Cannot deactivate yourself",
        )

    if not is_active and _is_last_active_super_admin(db, user):
        raise HTTPException(status_code=409, detail="Cannot disable the last active SUPER_ADMIN")

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
            "User status updated"
        ),
    )

    return user


def delete_user(
    db: Session,
    user_id: int,
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
        raise HTTPException(status_code=404, detail="User not found")

    target_role = db.query(Role).filter(Role.id == user.role_id).first()
    if actor_role_name != "SUPER_ADMIN" and target_role and target_role.name in {"SUPER_ADMIN", "ORGANIZATION_OWNER"}:
        raise HTTPException(status_code=403, detail="Target user cannot be deleted")

    if user.id == actor_user_id:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete yourself",
        )

    if _is_last_active_super_admin(db, user):
        raise HTTPException(status_code=409, detail="Cannot delete the last active SUPER_ADMIN")

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
            "User deleted"
        ),
    )

    return True
