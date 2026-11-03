from sqlalchemy.orm import Session

from app.models.lead import Lead

from app.core.tenant import tenant_filter


STAGE_WEIGHTS = {
    "NEW": 0.10,
    "CONTACTED": 0.25,
    "MEETING": 0.50,
    "PROPOSAL": 0.75,
    "WON": 1.00,
    "LOST": 0.00,
}


def calculate_forecast(
    db: Session,
    organization_id: int,
):
    leads = (
        tenant_filter(
            db.query(Lead),
            Lead,
            organization_id,
        )
        .all()
    )

    pipeline_value: float = 0
    weighted_revenue: float = 0
    won_revenue: int = 0

    total_leads = len(leads)
    won_count = 0

    for lead in leads:

        value = (
            lead.estimated_value
            or 0
        )

        stage = (
            lead.pipeline_stage
            or "NEW"
        )

        pipeline_value += value

        weight = STAGE_WEIGHTS.get(
            stage.upper(),
            0.10,
        )

        weighted_revenue += (
            value * weight
        )

        if stage.upper() == "WON":
            won_revenue += value
            won_count += 1

    close_rate: float = 0

    if total_leads > 0:
        close_rate = round(
            (won_count / total_leads) * 100,
            2,
        )

    annual_projection = (
        weighted_revenue * 12
    )

    return {
        "pipeline_value": pipeline_value,
        "weighted_revenue": round(
            weighted_revenue,
            2,
        ),
        "won_revenue": won_revenue,
        "forecast_revenue": round(
            weighted_revenue,
            2,
        ),
        "close_rate": close_rate,
        "annual_projection": round(
            annual_projection,
            2,
        ),
    }
