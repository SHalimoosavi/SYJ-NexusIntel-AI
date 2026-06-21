from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def log_event(
    db: Session,
    organization_id: int | None,
    user_id: int | None,
    event_type: str,
    resource_type: str | None = None,
    resource_id: int | None = None,
    description: str | None = None,
):
    audit = AuditLog(
        organization_id=organization_id,
        user_id=user_id,
        event_type=event_type,
        resource_type=resource_type,
        resource_id=resource_id,
        description=description,
    )

    db.add(audit)
    db.commit()

    db.refresh(audit)

    return audit


def get_audit_logs(
    db: Session,
    organization_id: int,
):
    return (
        db.query(AuditLog)
        .filter(
            AuditLog.organization_id
            == organization_id
        )
        .order_by(
            AuditLog.created_at.desc()
        )
        .all()
    )
