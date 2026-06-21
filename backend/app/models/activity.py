from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey

from app.database.database import Base


class Activity(Base):
    __tablename__ = "activities"

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

    lead_id = Column(
        Integer,
        ForeignKey("leads.id"),
        nullable=False,
    )

    activity_type = Column(
        String,
        nullable=False,
    )

    description = Column(
        String,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )
