from sqlalchemy.orm import Session

from app.models.lead import Lead

from app.services.revenue_forecast_service import (
    calculate_forecast
)


def generate_executive_briefing(
    db: Session
):

    forecast = calculate_forecast(db)

    pipeline_value = forecast[
        "pipeline_value"
    ]

    forecast_revenue = forecast[
        "forecast_revenue"
    ]

    annual_projection = forecast[
        "annual_projection"
    ]

    close_rate = forecast[
        "close_rate"
    ]

    executive_summary = (
        f"Current pipeline value is "
        f"${pipeline_value}. "
        f"Forecast revenue is "
        f"${forecast_revenue}. "
        f"Annual projection is "
        f"${annual_projection}."
    )

    if close_rate == 0:

        risk_summary = (
            "No closed deals detected. "
            "Revenue conversion risk is high."
        )

        recommendation = (
            "Focus on MEETING and "
            "PROPOSAL stage leads."
        )

    elif close_rate < 10:

        risk_summary = (
            "Low conversion rate detected."
        )

        recommendation = (
            "Improve follow-up process "
            "and proposal conversions."
        )

    else:

        risk_summary = (
            "Pipeline health is stable."
        )

        recommendation = (
            "Continue scaling lead generation."
        )

    return {
        "pipeline_value":
        pipeline_value,

        "forecast_revenue":
        forecast_revenue,

        "annual_projection":
        annual_projection,

        "close_rate":
        close_rate,

        "executive_summary":
        executive_summary,

        "risk_summary":
        risk_summary,

        "recommendation":
        recommendation
    }


def get_top_opportunities(
    db: Session
):

    leads = (
        db.query(Lead)
        .order_by(
            Lead.estimated_value.desc()
        )
        .limit(5)
        .all()
    )

    return [
        {
            "id": lead.id,
            "business_name":
            lead.business_name,

            "estimated_value":
            lead.estimated_value,

            "pipeline_stage":
            lead.pipeline_stage
        }
        for lead in leads
    ]


def get_risks(
    db: Session
):

    risks = []

    leads = db.query(Lead).all()

    if not leads:
        risks.append(
            "No leads available."
        )

    won_count = len(
        [
            l for l in leads
            if (
                l.pipeline_stage
                and
                l.pipeline_stage.upper()
                == "WON"
            )
        ]
    )

    if won_count == 0:
        risks.append(
            "No won deals detected."
        )

    stale_leads = len(
        [
            l for l in leads
            if not l.next_followup
        ]
    )

    if stale_leads > 0:
        risks.append(
            f"{stale_leads} leads have no follow-up scheduled."
        )

    return {
        "risk_count":
        len(risks),

        "risks":
        risks
    }
