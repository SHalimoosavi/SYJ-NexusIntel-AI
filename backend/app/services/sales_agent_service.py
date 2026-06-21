from sqlalchemy.orm import Session

from app.models.lead import Lead
from app.core.tenant import tenant_filter

PIPELINE_SCORES = {
    "NEW": 5,
    "CONTACTED": 10,
    "MEETING": 18,
    "PROPOSAL": 25,
    "WON": 25,
    "LOST": 0,
}


def get_priority(score: int):

    if score >= 80:
        return "HOT"

    if score >= 60:
        return "WARM"

    return "COLD"


def calculate_value_score(
    estimated_value: int
):

    if estimated_value >= 10000:
        return 40

    if estimated_value >= 5000:
        return 30

    if estimated_value >= 2500:
        return 20

    if estimated_value >= 1000:
        return 10

    return 5


def calculate_pipeline_score(
    stage: str
):

    return PIPELINE_SCORES.get(
        stage.upper(),
        5
    )


def calculate_opportunity_score(
    estimated_value: int
):

    if estimated_value >= 10000:
        return 20

    if estimated_value >= 5000:
        return 15

    if estimated_value >= 2500:
        return 12

    if estimated_value >= 1000:
        return 8

    return 3


def calculate_followup_score(
    lead
):

    if lead.next_followup:
        return 15

    return 0


def calculate_total_score(
    lead
):

    value_score = (
        calculate_value_score(
            lead.estimated_value or 0
        )
    )

    pipeline_score = (
        calculate_pipeline_score(
            lead.pipeline_stage or "NEW"
        )
    )

    opportunity_score = (
        calculate_opportunity_score(
            lead.estimated_value or 0
        )
    )

    followup_score = (
        calculate_followup_score(
            lead
        )
    )

    total = (
        value_score
        + pipeline_score
        + opportunity_score
        + followup_score
    )

    return min(total, 100)


def get_sales_priorities(
    db: Session,
    organization_id: int,
):

    leads = (
        tenant_filter(
            db.query(Lead),
            Lead,
            organization_id,
    )
    .order_by(
        Lead.estimated_value.desc()
    )
    .all()
    )

    results = []

    for lead in leads:

        score = (
            calculate_total_score(
                lead
            )
        )

        results.append({
            "id": lead.id,

            "business_name":
            lead.business_name,

            "estimated_value":
            lead.estimated_value or 0,

            "pipeline_stage":
            lead.pipeline_stage,

            "score":
            score,

            "priority":
            get_priority(score),

            "next_followup":
            lead.next_followup
        })

    return results


def generate_pitch(
    business_name: str,
    domain: str,
    lead_score: int
):

    priority = get_priority(
        lead_score
    )

    return {
        "business_name":
        business_name,

        "priority":
        priority,

        "sales_pitch":
        (
            f"{business_name} has "
            f"opportunities to improve "
            f"online visibility, security "
            f"and lead generation. "
            f"Our intelligence platform "
            f"identified actionable growth "
            f"areas for {domain}."
        )
    }


def generate_followup(
    business_name: str,
    pipeline_stage: str
):

    stage = (
        pipeline_stage.upper()
    )

    if stage == "NEW":

        action = (
            "Send introduction email."
        )

    elif stage == "CONTACTED":

        action = (
            "Schedule discovery call."
        )

    elif stage == "MEETING":

        action = (
            "Prepare proposal."
        )

    elif stage == "PROPOSAL":

        action = (
            "Follow up within 48 hours."
        )

    elif stage == "WON":

        action = (
            "Upsell and request referral."
        )

    else:

        action = (
            "Review account status."
        )

    return {
        "business_name":
        business_name,

        "pipeline_stage":
        pipeline_stage,

        "recommended_action":
        action
    }
