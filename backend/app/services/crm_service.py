from sqlalchemy.orm import Session

from app.models.lead import Lead

from app.core.tenant import tenant_filter


def get_crm_stats(
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

    total_leads = len(leads)

    hot_leads = len(
        [
            x
            for x in leads
            if x.priority == "HOT"
        ]
    )

    warm_leads = len(
        [
            x
            for x in leads
            if x.priority == "WARM"
        ]
    )

    cold_leads = len(
        [
            x
            for x in leads
            if x.priority == "COLD"
        ]
    )

    average_lead_score = 0

    if total_leads:
        average_lead_score = int(
            sum(
                lead.lead_score or 0
                for lead in leads
            )
            / total_leads
        )

    won_deals = len(
        [
            x
            for x in leads
            if x.pipeline_stage == "WON"
        ]
    )

    lost_deals = len(
        [
            x
            for x in leads
            if x.pipeline_stage == "LOST"
        ]
    )

    close_rate: float = 0.0

    if won_deals + lost_deals > 0:
        close_rate = round(
            (
                won_deals
                / (won_deals + lost_deals)
            )
            * 100,
            2,
        )

    return {
        "total_leads": total_leads,
        "hot_leads": hot_leads,
        "warm_leads": warm_leads,
        "cold_leads": cold_leads,
        "average_lead_score": average_lead_score,
        "won_deals": won_deals,
        "lost_deals": lost_deals,
        "close_rate": close_rate,
    }


def get_revenue_metrics(
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

    won_deals = len(
        [
            x
            for x in leads
            if x.pipeline_stage == "WON"
        ]
    )

    total_deals = len(leads)

    win_rate: float = 0.0

    if total_deals > 0:
        win_rate = round(
            (won_deals / total_deals) * 100,
            2,
        )

    average_deal_size = 0

    if total_deals > 0:
        average_deal_size = int(
            pipeline_value / total_deals
        )

    sales_velocity = int(
        (
            total_deals
            * average_deal_size
            * (win_rate / 100)
        )
        / 30
    )

    quarterly_projection = (
        forecast_revenue * 3
    )

    annual_projection = (
        forecast_revenue * 12
    )

    return {
        "pipeline_value": pipeline_value,
        "forecast_revenue": forecast_revenue,
        "won_revenue": won_revenue,
        "win_rate": win_rate,
        "average_deal_size": average_deal_size,
        "sales_velocity": sales_velocity,
        "quarterly_projection": quarterly_projection,
        "annual_projection": annual_projection,
    }


def get_pipeline_metrics(
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

    return {
        "new": len([x for x in leads if x.pipeline_stage == "NEW"]),
        "contacted": len([x for x in leads if x.pipeline_stage == "CONTACTED"]),
        "meeting": len([x for x in leads if x.pipeline_stage == "MEETING"]),
        "proposal": len([x for x in leads if x.pipeline_stage == "PROPOSAL"]),
        "negotiation": len([x for x in leads if x.pipeline_stage == "NEGOTIATION"]),
        "won": len([x for x in leads if x.pipeline_stage == "WON"]),
        "lost": len([x for x in leads if x.pipeline_stage == "LOST"]),
    }
