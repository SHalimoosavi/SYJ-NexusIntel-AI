from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.lead import Lead
from app.models.activity import Activity

from app.services.subscription_limit_service import (
    check_lead_limit,
)


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


def create_lead(
    db: Session,
    lead_data,
    organization_id: int,
):
    current_leads = (
        db.query(Lead)
        .filter(
            Lead.organization_id == organization_id
        )
        .count()
    )

    allowed = check_lead_limit(
        db,
        organization_id,
        current_leads,
    )

    if not allowed:
        raise HTTPException(
            status_code=403,
            detail=(
                "Lead limit reached. "
                "Upgrade your plan."
            ),
        )

    scoring = calculate_lead_score(
        lead_data.industry,
        lead_data.company_size,
        lead_data.estimated_value,
    )

    lead_payload = lead_data.model_dump()

    lead_payload["organization_id"] = organization_id

    lead = Lead(
        **lead_payload,
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
        organization_id,
    )

    return lead


def get_all_leads(
    db: Session,
    organization_id: int,
):
    return (
        db.query(Lead)
        .filter(
            Lead.organization_id == organization_id
        )
        .all()
    )


def get_lead(
    db: Session,
    lead_id: int,
    organization_id: int,
):
    return (
        db.query(Lead)
        .filter(
            Lead.id == lead_id,
            Lead.organization_id == organization_id,
        )
        .first()
    )


def update_lead_pipeline(
    db: Session,
    lead_id: int,
    data,
    organization_id: int,
):
    lead = get_lead(
        db,
        lead_id,
        organization_id,
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
            organization_id,
        )

    return lead


def delete_lead(
    db: Session,
    lead_id: int,
    organization_id: int,
):
    lead = get_lead(
        db,
        lead_id,
        organization_id,
    )

    if not lead:
        return False

    create_activity_log(
        db,
        lead.id,
        "LEAD_DELETED",
        f"Lead deleted: {lead.business_name}",
        organization_id,
    )

    db.delete(lead)
    db.commit()

    return True
