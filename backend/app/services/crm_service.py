from sqlalchemy.orm import Session

from app.models.lead import Lead


def get_crm_stats(db: Session):
    leads = db.query(Lead).all()

    hot_leads = len(
        [x for x in leads if x.priority == "HOT"]
    )

    warm_leads = len(
        [x for x in leads if x.priority == "WARM"]
    )

    cold_leads = len(
        [x for x in leads if x.priority == "COLD"]
    )

    avg_score = 0

    if leads:
        avg_score = int(
            sum(
                lead.lead_score or 0
                for lead in leads
            )
            / len(leads)
        )

    return {
        "total_leads": len(leads),
        "hot_leads": hot_leads,
        "warm_leads": warm_leads,
        "cold_leads": cold_leads,
        "average_lead_score": avg_score,
        "won_deals": len(
            [
                x
                for x in leads
                if x.pipeline_stage == "WON"
            ]
        ),
        "lost_deals": len(
            [
                x
                for x in leads
                if x.pipeline_stage == "LOST"
            ]
        ),
    }


def get_revenue_metrics(db: Session):
    leads = db.query(Lead).all()

    pipeline_value = sum(
        lead.estimated_value or 0
        for lead in leads
    )

    forecast_revenue = sum(
        int(
            (lead.estimated_value or 0)
            * (
                (lead.probability or 0)
                / 100
            )
        )
        for lead in leads
    )

    won_revenue = sum(
        lead.actual_revenue or 0
        for lead in leads
        if lead.pipeline_stage == "WON"
    )

    return {
        "pipeline_value": pipeline_value,
        "forecast_revenue": forecast_revenue,
        "won_revenue": won_revenue,
    }


def get_pipeline_metrics(db: Session):
    leads = db.query(Lead).all()

    return {
        "new": len(
            [
                x
                for x in leads
                if x.pipeline_stage == "NEW"
            ]
        ),
        "contacted": len(
            [
                x
                for x in leads
                if x.pipeline_stage == "CONTACTED"
            ]
        ),
        "meeting": len(
            [
                x
                for x in leads
                if x.pipeline_stage == "MEETING"
            ]
        ),
        "proposal": len(
            [
                x
                for x in leads
                if x.pipeline_stage == "PROPOSAL"
            ]
        ),
        "negotiation": len(
            [
                x
                for x in leads
                if x.pipeline_stage == "NEGOTIATION"
            ]
        ),
        "won": len(
            [
                x
                for x in leads
                if x.pipeline_stage == "WON"
            ]
        ),
        "lost": len(
            [
                x
                for x in leads
                if x.pipeline_stage == "LOST"
            ]
        ),
    }
