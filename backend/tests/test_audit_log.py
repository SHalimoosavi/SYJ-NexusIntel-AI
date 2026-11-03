import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.redaction import redact_text
from app.database.database import Base
from app.models.audit_log import AuditLog


def test_redaction_removes_email_bearer_and_jwt():
    value = (
        "user alice@example.invalid used Bearer abcdefghijklmnopqrstuvwxyz "
        "and eyJabcdefgh.abcdefgh.abcdefgh"
    )
    redacted = redact_text(value)
    assert "alice@example.invalid" not in redacted
    assert "abcdefghijklmnopqrstuvwxyz" not in redacted
    assert "eyJabcdefgh" not in redacted


def test_audit_log_is_append_only_at_orm_layer():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    try:
        record = AuditLog(
            organization_id=None,
            user_id=None,
            event_type="TEST_EVENT",
            description="safe",
        )
        session.add(record)
        session.commit()
        record.description = "tampered"
        with pytest.raises(ValueError, match="append-only"):
            session.commit()
        session.rollback()

        with pytest.raises(ValueError, match="append-only"):
            session.delete(record)
            session.commit()
        session.rollback()
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
