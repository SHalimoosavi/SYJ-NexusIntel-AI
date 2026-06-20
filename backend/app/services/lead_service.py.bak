from sqlalchemy.orm import Session

from app.models.lead import Lead


def create_lead(
    db: Session,
    lead_data
):
    lead = Lead(**lead_data.dict())

    db.add(lead)

    db.commit()

    db.refresh(lead)

    return lead


def get_all_leads(
    db: Session
):
    return db.query(Lead).all()


def delete_lead(
    db: Session,
    lead_id: int
):
    lead = db.query(Lead).filter(
        Lead.id == lead_id
    ).first()

    if not lead:
        return False

    db.delete(lead)

    db.commit()

    return True
