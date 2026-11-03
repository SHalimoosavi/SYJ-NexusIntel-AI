from app.core.clock import utcnow_naive

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime

from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    name = Column(
        String,
        nullable=False,
        unique=True,
    )

    slug = Column(
        String,
        nullable=False,
        unique=True,
    )

    plan = Column(
        String,
        default="FREE",
    )

    max_users = Column(
        Integer,
        default=3,
    )

    max_leads = Column(
        Integer,
        default=100,
    )

    max_ai_requests = Column(
        Integer,
        default=100,
    )

    created_at = Column(
        DateTime,
        default=utcnow_naive,
    )
