from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.models.activity import Activity
from app.models.lead import Lead

from app.core.tenant import (
    tenant_filter,
)


def create_activity(
    db: Session,
    activity_data,
    organization_id: int,
):
    lead = (
        db.query(Lead)
        .filter(
            Lead.id == activity_data.lead_id,
            Lead.organization_id == organization_id,
        )
        .first()
    )

    if not lead:
        raise HTTPException(
            status_code=404,
            detail="Lead not found",
        )

    activity = Activity(
        lead_id=activity_data.lead_id,
        activity_type=activity_data.activity_type,
        description=activity_data.description,
        organization_id=organization_id,
    )

    db.add(activity)

    db.commit()

    db.refresh(activity)

    return activity


def get_lead_activities(
    db: Session,
    lead_id: int,
    organization_id: int,
):
    return (
        tenant_filter(
            db.query(Activity),
            Activity,
            organization_id,
        )
        .filter(
            Activity.lead_id == lead_id
        )
        .order_by(
            Activity.created_at.desc()
        )
        .all()
    )


def create_system_activity(
    db: Session,
    lead_id: int,
    activity_type: str,
    description: str,
    organization_id: int,
):
    lead = (
        db.query(Lead)
        .filter(
            Lead.id == lead_id,
            Lead.organization_id == organization_id,
        )
        .first()
    )
    if lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")

    activity = Activity(
        lead_id=lead_id,
        activity_type=activity_type,
        description=description,
        organization_id=organization_id,
    )

    db.add(activity)

    db.commit()

    return activity
