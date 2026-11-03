from datetime import datetime

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey

from sqlalchemy.orm import Mapped

from app.database.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    full_name = Column(
        String,
        nullable=False,
    )

    email = Column(
        String,
        unique=True,
        nullable=False,
    )

    hashed_password: Mapped[str] = Column(
        String,
        nullable=False,
    )

    organization_id: Mapped[int | None] = Column(
        Integer,
        ForeignKey("organizations.id"),
        nullable=True,
    )

    role_id = Column(
        Integer,
        ForeignKey("roles.id"),
        nullable=True,
    )

    is_active = Column(
        Boolean,
        default=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )
