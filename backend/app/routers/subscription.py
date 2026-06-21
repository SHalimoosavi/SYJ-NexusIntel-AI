from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.schemas.subscription import (
    SubscriptionCreate,
    SubscriptionResponse,
)

from app.services.subscription_service import (
    create_subscription,
    get_subscription,
    get_subscriptions,
)

router = APIRouter(
    prefix="/subscriptions",
    tags=["Subscriptions"],
)


@router.post(
    "",
    response_model=SubscriptionResponse,
)
def create_subscription_route(
    subscription: SubscriptionCreate,
    db: Session = Depends(get_db),
):
    return create_subscription(
        db,
        subscription.organization_id,
        subscription.plan_name,
    )


@router.get(
    "",
    response_model=list[SubscriptionResponse],
)
def get_subscriptions_route(
    db: Session = Depends(get_db),
):
    return get_subscriptions(db)


@router.get(
    "/{organization_id}",
    response_model=SubscriptionResponse,
)
def get_subscription_route(
    organization_id: int,
    db: Session = Depends(get_db),
):
    return get_subscription(
        db,
        organization_id,
    )
