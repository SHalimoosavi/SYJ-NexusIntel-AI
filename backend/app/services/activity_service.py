from sqlalchemy.orm import Session

from app.models.activity import Activity


def create_activity(
    db: Session,
    activity_data,
):
    activity = Activity(
        **activity_data.model_dump()
    )

    db.add(activity)
    db.commit()
    db.refresh(activity)

    return activity


def get_lead_activities(
    db: Session,
    lead_id: int,
):
    return (
        db.query(Activity)
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
):
    activity = Activity(
        lead_id=lead_id,
        activity_type=activity_type,
        description=description,
    )

    db.add(activity)
    db.commit()

    return activity
