from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.models.user import User


def get_current_organization(
    user_id: int,
    db: Session,
):
    user = (
        db.query(User)
        .filter(
            User.id == user_id
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    if not user.organization_id:
        raise HTTPException(
            status_code=403,
            detail=(
                "User not assigned "
                "to organization"
            ),
        )

    return user.organization_id


def tenant_filter(
    query,
    model,
    organization_id: int,
):
    return (
        query.filter(
            model.organization_id
            == organization_id
        )
    )


def validate_tenant_access(
    record,
    organization_id: int,
):
    if not record:
        return False

    if (
        record.organization_id
        != organization_id
    ):
        raise HTTPException(
            status_code=403,
            detail=(
                "Tenant access denied"
            ),
        )

    return True
