from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.rbac import require_roles
from app.database.database import get_db
from app.schemas.subscription import SubscriptionCreate, SubscriptionResponse
from app.services.subscription_service import (
    create_subscription,
    get_subscription,
    get_subscriptions,
)

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


@router.post("", response_model=SubscriptionResponse)
def create_subscription_route(
    subscription: SubscriptionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["SUPER_ADMIN"])),
):
    return create_subscription(
        db,
        subscription.organization_id,
        subscription.plan_name,
        current_user["user_id"],
    )


@router.get("", response_model=list[SubscriptionResponse])
def get_subscriptions_route(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["SUPER_ADMIN"])),
):
    return get_subscriptions(db)


@router.get("/{organization_id}", response_model=SubscriptionResponse)
def get_subscription_route(
    organization_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(["SUPER_ADMIN", "ORGANIZATION_OWNER", "MANAGER"])
    ),
):
    if (
        current_user["role_name"] != "SUPER_ADMIN"
        and current_user["organization_id"] != organization_id
    ):
        raise HTTPException(status_code=404, detail="Subscription not found")
    subscription = get_subscription(db, organization_id)
    if subscription is None:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return subscription
