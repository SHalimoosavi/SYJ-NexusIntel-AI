from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey

from app.database.database import Base


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Column[int] = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    organization_id = Column(
        Integer,
        ForeignKey("organizations.id"),
        nullable=False,
    )

    plan_name = Column(
        String,
        nullable=False,
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

    max_whatsapp_campaigns = Column(
        Integer,
        default=0,
    )

    max_email_campaigns = Column(
        Integer,
        default=0,
    )

    status = Column(
        String,
        default="ACTIVE",
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )
