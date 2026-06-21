from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String

from app.database.database import Base


class Role(Base):
    __tablename__ = "roles"

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
