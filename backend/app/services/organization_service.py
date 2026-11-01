from sqlalchemy.orm import Session

from app.models.organization import Organization
from app.services.audit_service import log_event
from app.services.feature_flag_service import seed_default_features
from app.services.subscription_service import create_subscription


def create_organization(db: Session, organization_data, actor_user_id: int | None = None):
    organization = Organization(**organization_data.model_dump())
    db.add(organization)
    db.commit()
    db.refresh(organization)
    create_subscription(db=db, organization_id=organization.id, plan_name="FREE")
    seed_default_features(db, organization.id)
    log_event(
        db=db,
        organization_id=organization.id,
        user_id=actor_user_id,
        event_type="ORGANIZATION_CREATED",
        resource_type="ORGANIZATION",
        resource_id=organization.id,
        description=f"Organization created: {organization.name}",
    )
    return organization


def get_organizations(db: Session, organization_id: int | None = None):
    query = db.query(Organization)
    if organization_id is not None:
        query = query.filter(Organization.id == organization_id)
    return query.order_by(Organization.id.desc()).all()


def get_organization(
    db: Session,
    organization_id: int,
    tenant_organization_id: int | None = None,
):
    query = db.query(Organization).filter(Organization.id == organization_id)
    if tenant_organization_id is not None:
        query = query.filter(Organization.id == tenant_organization_id)
    return query.first()
