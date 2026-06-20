from sqlalchemy.orm import Session

from app.models.lead import Lead


def calculate_lead_score(
    lead_data
):
    score = 0

    if lead_data.email:
        score += 15

    if lead_data.phone:
        score += 15

    if lead_data.website:
        score += 15

    if lead_data.city:
        score += 10

    if lead_data.category:
        score += 10

    if lead_data.industry:
        score += 10

    if lead_data.company_size:
        score += 10

    if lead_data.estimated_value >= 100000:
        score += 15

    return min(score, 100)


def calculate_priority(
    score: int
):
    if score >= 80:
        return "HOT"

    if score >= 50:
        return "WARM"

    return "COLD"


def create_lead(
    db: Session,
    lead_data
):
    score = calculate_lead_score(
        lead_data
    )

    priority = calculate_priority(
        score
    )

    lead = Lead(
        **lead_data.model_dump(),
        lead_score=score,
        priority=priority
    )

    db.add(lead)

    db.commit()

    db.refresh(lead)

    return lead


def get_all_leads(
    db: Session
):
    return (
        db.query(Lead)
        .order_by(
            Lead.lead_score.desc()
        )
        .all()
    )


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
    lead.pipeline_stage = data.pipeline_stage

    lead.estimated_value = (
        data.estimated_value
    )

    lead.probability = (
        data.probability
    )

    lead.actual_revenue = (
        data.actual_revenue
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
