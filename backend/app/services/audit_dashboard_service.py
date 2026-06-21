from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


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


def get_event_summary(
    db: Session,
    organization_id: int,
):
    logs = (
        db.query(AuditLog)
        .filter(
            AuditLog.organization_id
            == organization_id
        )
        .all()
    )

    summary = {}

    for log in logs:
        summary[log.event_type] = (
            summary.get(
                log.event_type,
                0,
            )
            + 1
        )

    return summary
