from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey

from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class Invitation(Base):
    __tablename__ = "invitations"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    organization_id = Column(
        Integer,
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )

    email = Column(
        String,
        nullable=False,
        index=True,
    )

    role_id = Column(
        Integer,
        ForeignKey("roles.id"),
        nullable=False,
    )

    token = Column(
        String,
        nullable=False,
        unique=True,
        index=True,
    )

    is_used = Column(
        Boolean,
        default=False,
    )

    expires_at = Column(
        DateTime,
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )
