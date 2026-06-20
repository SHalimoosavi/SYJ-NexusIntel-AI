from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime

from app.database.database import Base


class OSINTReport(Base):
    __tablename__ = "osint_reports"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    domain = Column(
        String,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )
