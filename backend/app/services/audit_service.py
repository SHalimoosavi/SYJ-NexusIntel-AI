import logging

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.organization import Organization
from app.models.user import User
from app.models.role import Role
from app.core.redaction import redact_text

logger = logging.getLogger("security.audit")


def log_event(
    db: Session,
    organization_id: int | None,
    user_id: int | None,
    event_type: str,
    resource_type: str | None = None,
    resource_id: int | None = None,
    description: str | None = None,
):
    try:
        audit = AuditLog(
            organization_id=organization_id,
            user_id=user_id,
            event_type=event_type,
            resource_type=resource_type,
            resource_id=resource_id,
            description=redact_text(description),
        )
        db.add(audit)
        db.commit()
        db.refresh(audit)
        return audit
    except Exception as exc:
        db.rollback()
        # Never log the exception string or SQL parameters: they may contain PII.
        logger.error("audit_log_write_failed error_type=%s", type(exc).__name__)
        return None


def get_audit_logs(db: Session, organization_id: int):
    return (
        db.query(AuditLog)
        .filter(AuditLog.organization_id == organization_id)
        .order_by(AuditLog.created_at.desc())
        .all()
    )
