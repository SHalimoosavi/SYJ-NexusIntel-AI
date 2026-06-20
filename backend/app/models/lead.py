from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime

from app.database.database import Base


class Lead(Base):
    __tablename__ = "leads"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    business_name = Column(
        String,
        nullable=False
    )

    contact_person = Column(
        String,
        nullable=True
    )

    email = Column(
        String,
        nullable=True
    )

    phone = Column(
        String,
        nullable=True
    )

    website = Column(
        String,
        nullable=True
    )

    city = Column(
        String,
        nullable=True
    )

    category = Column(
        String,
        nullable=True
    )

    industry = Column(
        String,
        nullable=True
    )

    company_size = Column(
        String,
        nullable=True
    )

    notes = Column(
        String,
        nullable=True
    )

    source = Column(
        String,
        nullable=True
    )

    status = Column(
        String,
        default="NEW"
    )

    pipeline_stage = Column(
        String,
        default="NEW"
    )

    estimated_value = Column(
        Integer,
        default=0
    )

    lead_score = Column(
        Integer,
        default=0
    )

    priority = Column(
        String,
        default="COLD"
    )

    probability = Column(
        Integer,
        default=10
    )

    actual_revenue = Column(
        Integer,
        default=0
    )

    last_contacted = Column(
        String,
        nullable=True
    )

    next_followup = Column(
        String,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )
