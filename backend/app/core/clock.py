"""UTC clock helpers for timezone-naive database timestamp columns.

The schema currently uses SQLAlchemy DateTime columns without timezone=True.
Generate the instant from an aware UTC clock, then normalize to naive UTC at the
persistence boundary so SQLite and PostgreSQL compare consistently.
"""
from datetime import datetime, timezone


def utcnow_naive() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)
