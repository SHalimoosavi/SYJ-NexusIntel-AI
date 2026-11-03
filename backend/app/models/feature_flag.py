from app.core.clock import utcnow_naive

from sqlalchemy import Column
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey

from app.database.database import Base


class FeatureFlag(Base):
    __tablename__ = "feature_flags"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    organization_id = Column(
        Integer,
        ForeignKey("organizations.id"),
        nullable=False,
    )

    feature_name = Column(
        String,
        nullable=False,
    )

    is_enabled: Mapped[bool | None] = mapped_column(
        Boolean,
        default=False,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=utcnow_naive,
    )
