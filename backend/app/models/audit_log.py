from app.core.clock import utcnow_naive

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey, event

from app.database.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    organization_id = Column(
        Integer,
        ForeignKey("organizations.id"),
        nullable=True,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )

    event_type = Column(
        String,
        nullable=False,
        index=True,
    )

    resource_type = Column(
        String,
        nullable=True,
    )

    resource_id = Column(
        Integer,
        nullable=True,
    )

    description = Column(
        String,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=utcnow_naive,
    )


@event.listens_for(AuditLog, "before_update")
def prevent_audit_log_update(_mapper, _connection, _target):
    raise ValueError("Audit log records are append-only")


@event.listens_for(AuditLog, "before_delete")
def prevent_audit_log_delete(_mapper, _connection, _target):
    raise ValueError("Audit log records are append-only")
