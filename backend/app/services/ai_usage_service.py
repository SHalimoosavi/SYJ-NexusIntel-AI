from datetime import datetime
from datetime import timedelta
import os

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.ai_usage import AIUsage
from app.models.subscription import Subscription

from app.services.audit_service import (
    log_event,
)


def get_subscription(
    db: Session,
    organization_id: int,
):
    return (
        db.query(Subscription)
        .filter(
            Subscription.organization_id
            == organization_id
        )
        .first()
    )


def count_ai_requests(
    db: Session,
    organization_id: int,
):
    start_date = (
        datetime.utcnow()
        - timedelta(days=30)
    )

    return (
        db.query(AIUsage)
        .filter(
            AIUsage.organization_id
            == organization_id,
            AIUsage.created_at >= start_date,
        )
        .count()
    )


def enforce_ai_limit(
    db: Session,
    organization_id: int,
):
    # Explicit development-only bypass. Unset APP_ENV defaults to production,
    # so a forgotten bypass flag can never silently disable paid-plan limits.
    app_env = os.getenv("APP_ENV", "production").lower()
    bypass_requested = os.getenv("AI_LIMIT_BYPASS", "false").lower() == "true"
    if bypass_requested and app_env in {"development", "dev", "local", "test"}:
        return

    subscription = get_subscription(
        db,
        organization_id,
    )

    if not subscription:
        raise HTTPException(
            status_code=403,
            detail="No subscription found",
        )

    current_usage = count_ai_requests(
        db,
        organization_id,
    )

    if (
        current_usage
        >= subscription.max_ai_requests
    ):
        raise HTTPException(
            status_code=403,
            detail=(
                "AI request limit reached. "
                "Upgrade your subscription."
            ),
        )


def log_ai_request(
    db: Session,
    organization_id: int,
    request_type: str,
    actor_user_id: int | None = None,
):
    usage = AIUsage(
        organization_id=organization_id,
        request_type=request_type,
    )

    db.add(usage)

    db.commit()

    db.refresh(usage)

    log_event(
        db=db,
        organization_id=organization_id,
        user_id=actor_user_id,
        event_type="AI_REQUEST",
        resource_type="AI_USAGE",
        resource_id=usage.id,
        description=request_type,
    )

    return usage
