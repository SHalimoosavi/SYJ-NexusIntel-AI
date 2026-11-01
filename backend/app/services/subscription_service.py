from sqlalchemy.orm import Session

from app.models.subscription import Subscription

from app.services.plan_catalog import get_plan

from app.services.audit_service import (
    log_event,
)


def create_subscription(
    db: Session,
    organization_id: int,
    plan_name: str = "FREE",
    actor_user_id: int | None = None,
):
    plan = get_plan(plan_name)

    if not plan:
        raise ValueError(
            f"Unknown subscription plan: {plan_name}"
        )

    subscription = Subscription(
        organization_id=organization_id,
        plan_name=plan_name,

        max_users=plan["max_users"],
        max_leads=plan["max_leads"],
        max_ai_requests=plan["max_ai_requests"],

        max_whatsapp_campaigns=
        plan["max_whatsapp_campaigns"],

        max_email_campaigns=
        plan["max_email_campaigns"],
    )

    db.add(subscription)

    db.commit()

    db.refresh(subscription)

    log_event(
        db=db,
        organization_id=organization_id,
        user_id=actor_user_id,
        event_type="SUBSCRIPTION_CREATED",
        resource_type="SUBSCRIPTION",
        resource_id=subscription.id,
        description=(
            f"Subscription created: "
            f"{plan_name}"
        ),
    )

    return subscription


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


def get_subscriptions(
    db: Session,
):
    return (
        db.query(Subscription)
        .order_by(
            Subscription.id.desc()
        )
        .all()
    )


def update_subscription_plan(
    db: Session,
    organization_id: int,
    plan_name: str,
):
    subscription = get_subscription(
        db,
        organization_id,
    )

    if not subscription:
        return None

    plan = get_plan(plan_name)

    if not plan:
        raise ValueError(
            f"Unknown subscription plan: {plan_name}"
        )

    old_plan = subscription.plan_name

    subscription.plan_name = plan_name

    subscription.max_users = plan["max_users"]
    subscription.max_leads = plan["max_leads"]
    subscription.max_ai_requests = plan["max_ai_requests"]

    subscription.max_whatsapp_campaigns = (
        plan["max_whatsapp_campaigns"]
    )

    subscription.max_email_campaigns = (
        plan["max_email_campaigns"]
    )

    db.commit()

    db.refresh(subscription)

    log_event(
        db=db,
        organization_id=organization_id,
        user_id=None,
        event_type="SUBSCRIPTION_UPDATED",
        resource_type="SUBSCRIPTION",
        resource_id=subscription.id,
        description=(
            f"Plan changed from "
            f"{old_plan} to {plan_name}"
        ),
    )

    return subscription
