from sqlalchemy.orm import Session

from app.models.lead import Lead


def create_lead(
    db: Session,
    lead_data
):
    lead = Lead(
        **lead_data.model_dump()
    )

    db.add(lead)

    db.commit()

    db.refresh(lead)

    return lead


def get_all_leads(
    db: Session
):
    return db.query(Lead).all()


def get_lead(
    db: Session,
    lead_id: int
):
    return (
        db.query(Lead)
        .filter(
            Lead.id == lead_id
        )
        .first()
    )


def update_lead_pipeline(
    db: Session,
    lead_id: int,
    data
):
    lead = get_lead(
        db,
        lead_id
    )

    if not lead:
        return None

    lead.status = data.status
    lead.pipeline_stage = (
        data.pipeline_stage
    )

    lead.estimated_value = (
        data.estimated_value
    )

    lead.last_contacted = (
        data.last_contacted
    )

    lead.next_followup = (
        data.next_followup
    )

    db.commit()

    db.refresh(lead)

    return lead


def delete_lead(
    db: Session,
    lead_id: int
):
    lead = get_lead(
        db,
        lead_id
    )

    if not lead:
        return False

    db.delete(lead)

    db.commit()

    return True
