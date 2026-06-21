from sqlalchemy.orm import Session

from app.models.lead import Lead
from app.models.activity import Activity


def calculate_lead_score(
    industry: str | None,
    company_size: str | None,
    estimated_value: int,
):
    score = 0

    high_value_industries = [
        "Healthcare",
        "Finance",
        "Technology",
        "Manufacturing",
    ]

    medium_value_industries = [
        "Education",
        "Retail",
        "Hospitality",
    ]

    if industry in high_value_industries:
        score += 30

    elif industry in medium_value_industries:
        score += 20

    else:
        score += 10

    if company_size == "ENTERPRISE":
        score += 30

    elif company_size == "MEDIUM":
        score += 20

    elif company_size == "SMALL":
        score += 10

    if estimated_value >= 1000000:
        score += 40

    elif estimated_value >= 500000:
        score += 30

    elif estimated_value >= 100000:
        score += 20

    else:
        score += 10

    score = min(score, 100)

    if score >= 80:
        priority = "HOT"
        probability = 80

    elif score >= 50:
        priority = "WARM"
        probability = 50

    else:
        priority = "COLD"
        probability = 20

    return {
        "score": score,
        "priority": priority,
        "probability": probability,
    }


def create_activity_log(
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


def create_lead(
    db: Session,
    lead_data,
):
    scoring = calculate_lead_score(
        lead_data.industry,
        lead_data.company_size,
        lead_data.estimated_value,
    )

    lead = Lead(
        **lead_data.model_dump(),
        lead_score=scoring["score"],
        priority=scoring["priority"],
        probability=scoring["probability"],
    )

    db.add(lead)
    db.commit()
    db.refresh(lead)

    create_activity_log(
        db,
        lead.id,
        "LEAD_CREATED",
        f"Lead created: {lead.business_name}",
    )

    return lead


def get_all_leads(
    db: Session,
):
    return db.query(Lead).all()


def get_lead(
    db: Session,
    lead_id: int,
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
    data,
):
    lead = get_lead(
        db,
        lead_id,
    )

    if not lead:
        return None

    previous_stage = lead.pipeline_stage

    lead.status = data.status
    lead.pipeline_stage = data.pipeline_stage
    lead.estimated_value = data.estimated_value
    lead.probability = data.probability
    lead.actual_revenue = data.actual_revenue
    lead.last_contacted = data.last_contacted
    lead.next_followup = data.next_followup

    db.commit()
    db.refresh(lead)

    if previous_stage != lead.pipeline_stage:
        create_activity_log(
            db,
            lead.id,
            "STAGE_CHANGED",
            f"{previous_stage} → {lead.pipeline_stage}",
        )

    return lead


def delete_lead(
    db: Session,
    lead_id: int,
):
    lead = get_lead(
        db,
        lead_id,
    )

    if not lead:
        return False

    create_activity_log(
        db,
        lead.id,
        "LEAD_DELETED",
        f"Lead deleted: {lead.business_name}",
    )

    db.delete(lead)
    db.commit()

    return True
