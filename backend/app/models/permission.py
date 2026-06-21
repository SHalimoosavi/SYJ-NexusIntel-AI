from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String

from app.database.database import Base


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    name = Column(
        String,
        nullable=False,
        unique=True,
    )

    description = Column(
        String,
        nullable=True,
    )
