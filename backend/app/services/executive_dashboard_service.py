from sqlalchemy.orm import Session

from app.models.user import User
from app.models.lead import Lead
from app.models.invitation import Invitation
from app.models.subscription import Subscription
from app.models.ai_usage import AIUsage

from app.services.crm_service import (
    get_crm_stats,
)

from app.services.revenue_forecast_service import (
    calculate_forecast,
)


def get_executive_dashboard(
    db: Session,
    organization_id: int,
):
    users = (
        db.query(User)
        .filter(
            User.organization_id
            == organization_id
        )
        .count()
    )

    active_users = (
        db.query(User)
        .filter(
            User.organization_id
            == organization_id,
            User.is_active.is_(True),
        )
        .count()
    )

    leads = (
        db.query(Lead)
        .filter(
            Lead.organization_id
            == organization_id
        )
        .count()
    )

    invitations = (
        db.query(Invitation)
        .filter(
            Invitation.organization_id
            == organization_id
        )
        .count()
    )

    accepted_invitations = (
        db.query(Invitation)
        .filter(
            Invitation.organization_id
            == organization_id,
            Invitation.is_used.is_(True),
        )
        .count()
    )

    ai_usage = (
        db.query(AIUsage)
        .filter(
            AIUsage.organization_id
            == organization_id
        )
        .count()
    )

    subscription = (
        db.query(Subscription)
        .filter(
            Subscription.organization_id
            == organization_id
        )
        .first()
    )

    crm = get_crm_stats(
        db,
        organization_id,
    )

    forecast = calculate_forecast(
        db,
        organization_id,
    )

    return {
        "organization_id": organization_id,
        "users": users,
        "active_users": active_users,
        "leads": leads,
        "invitations": invitations,
        "accepted_invitations": accepted_invitations,
        "ai_usage": ai_usage,
        "subscription": (
            subscription.plan_name
            if subscription
            else None
        ),
        "crm": crm,
        "forecast": forecast,
    }
