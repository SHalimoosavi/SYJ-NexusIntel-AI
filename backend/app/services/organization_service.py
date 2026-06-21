from sqlalchemy.orm import Session

from app.models.organization import Organization

from app.services.feature_flag_service import (
    seed_default_features,
)

from app.services.subscription_service import (
    create_subscription,
)

from app.services.audit_service import (
    log_event,
)


def create_organization(
    db: Session,
    organization_data,
):
    organization = Organization(
        **organization_data.model_dump()
    )

    db.add(organization)

    db.commit()

    db.refresh(organization)

    create_subscription(
        db=db,
        organization_id=organization.id,
        plan_name="FREE",
    )

    seed_default_features(
        db,
        organization.id,
    )

    log_event(
        db=db,
        organization_id=organization.id,
        user_id=None,
        event_type="ORGANIZATION_CREATED",
        resource_type="ORGANIZATION",
        resource_id=organization.id,
        description=f"Organization created: {organization.name}",
    )

    return organization


def get_organizations(
    db: Session,
):
    return (
        db.query(Organization)
        .order_by(
            Organization.id.desc()
        )
        .all()
    )


def get_organization(
    db: Session,
    organization_id: int,
):
    return (
        db.query(Organization)
        .filter(
            Organization.id
            == organization_id
        )
        .first()
    )
