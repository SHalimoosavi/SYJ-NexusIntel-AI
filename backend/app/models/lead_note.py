from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey

from app.database.database import Base


class LeadNote(Base):
    __tablename__ = "lead_notes"

    id: Column[int] = Column(
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

    lead_id = Column(
        Integer,
        ForeignKey("leads.id"),
        nullable=False,
    )

    note = Column(
        String,
        nullable=False,
    )

    note_type = Column(
        String,
        default="GENERAL",
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )
