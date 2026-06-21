from sqlalchemy.orm import Session

from app.models.lead import Lead


def get_crm_stats(db: Session):
    leads = db.query(Lead).all()

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
        average_lead_score = round(
            sum(
                lead.lead_score or 0
                for lead in leads
            )
            / total_leads
        )

    pipeline_health = round(
        (
            average_lead_score * 0.7
        )
        +
        (
            warm_leads * 2
        )
    )

    return {
        "total_leads": total_leads,
        "hot_leads": hot_leads,
        "warm_leads": warm_leads,
        "cold_leads": cold_leads,
        "average_lead_score": average_lead_score,
        "pipeline_health": pipeline_health,
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
        round(
            (
                lead.estimated_value or 0
            )
            *
            (
                lead.probability or 0
            )
            / 100
        )
        for lead in leads
    )

    won_revenue = sum(
        lead.actual_revenue or 0
        for lead in leads
        if lead.pipeline_stage == "WON"
    )

    sales_velocity = 0

    if leads:
        sales_velocity = round(
            pipeline_value / len(leads)
        )

    return {
        "pipeline_value": pipeline_value,
        "forecast_revenue": forecast_revenue,
        "won_revenue": won_revenue,
        "sales_velocity": sales_velocity,
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


def get_followup_queue(db: Session):
    leads = db.query(Lead).all()

    queue = []

    for lead in leads:

        if (
            lead.pipeline_stage == "CONTACTED"
            or lead.pipeline_stage == "MEETING"
            or lead.next_followup
        ):
            queue.append(
                {
                    "id": lead.id,
                    "business_name": lead.business_name,
                    "contact_person": lead.contact_person,
                    "lead_score": lead.lead_score,
                    "priority": lead.priority,
                    "next_followup": lead.next_followup,
                }
            )

    return queue
