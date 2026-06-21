from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey

from app.database.database import Base


class AgentMemory(Base):
    __tablename__ = "agent_memory"

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

    domain = Column(
        String,
        nullable=False,
        index=True,
    )

    overall_score = Column(
        Integer,
        default=0,
    )

    priority = Column(
        String,
        default="UNKNOWN",
    )

    estimated_value = Column(
        String,
        nullable=True,
    )

    analysis_data = Column(
        String,
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )
