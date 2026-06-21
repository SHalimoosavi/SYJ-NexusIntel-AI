from sqlalchemy.orm import Session

from app.models.subscription import Subscription


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


def check_user_limit(
    db: Session,
    organization_id: int,
    current_users: int,
):
    subscription = get_subscription(
        db,
        organization_id,
    )

    if not subscription:
        return False

    return (
        current_users
        < subscription.max_users
    )


def check_lead_limit(
    db: Session,
    organization_id: int,
    current_leads: int,
):
    subscription = get_subscription(
        db,
        organization_id,
    )

    if not subscription:
        return False

    return (
        current_leads
        < subscription.max_leads
    )


def check_ai_limit(
    db: Session,
    organization_id: int,
    current_requests: int,
):
    subscription = get_subscription(
        db,
        organization_id,
    )

    if not subscription:
        return False

    return (
        current_requests
        < subscription.max_ai_requests
    )


def check_whatsapp_limit(
    db: Session,
    organization_id: int,
    current_campaigns: int,
):
    subscription = get_subscription(
        db,
        organization_id,
    )

    if not subscription:
        return False

    return (
        current_campaigns
        < subscription.max_whatsapp_campaigns
    )


def check_email_limit(
    db: Session,
    organization_id: int,
    current_campaigns: int,
):
    subscription = get_subscription(
        db,
        organization_id,
    )

    if not subscription:
        return False

    return (
        current_campaigns
        < subscription.max_email_campaigns
    )
