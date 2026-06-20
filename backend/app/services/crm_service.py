from sqlalchemy.orm import Session

from app.models.lead import Lead


def get_crm_stats(db: Session):

    leads = db.query(Lead).all()

    return {
        "total_leads": len(leads),

        "new_leads":
        len([
            x for x in leads
            if x.status == "NEW"
        ]),

        "contacted_leads":
        len([
            x for x in leads
            if x.status == "CONTACTED"
        ]),

        "meeting_leads":
        len([
            x for x in leads
            if x.pipeline_stage == "MEETING"
        ]),

        "proposal_leads":
        len([
            x for x in leads
            if x.pipeline_stage == "PROPOSAL"
        ]),

        "won_deals":
        len([
            x for x in leads
            if x.pipeline_stage == "WON"
        ]),

        "lost_deals":
        len([
            x for x in leads
            if x.pipeline_stage == "LOST"
        ])
    }


def get_revenue_metrics(db: Session):

    leads = db.query(Lead).all()

    pipeline_value = sum(
        lead.estimated_value or 0
        for lead in leads
    )

    won_revenue = sum(
        lead.estimated_value or 0
        for lead in leads
        if lead.pipeline_stage == "WON"
    )

    forecast_revenue = int(
        pipeline_value * 0.4
    )

    return {
        "pipeline_value":
        pipeline_value,

        "won_revenue":
        won_revenue,

        "forecast_revenue":
        forecast_revenue
    }


def get_pipeline_metrics(db: Session):

    leads = db.query(Lead).all()

    return {
        "new":
        len([
            x for x in leads
            if x.pipeline_stage == "NEW"
        ]),

        "contacted":
        len([
            x for x in leads
            if x.pipeline_stage == "CONTACTED"
        ]),

        "meeting":
        len([
            x for x in leads
            if x.pipeline_stage == "MEETING"
        ]),

        "proposal":
        len([
            x for x in leads
            if x.pipeline_stage == "PROPOSAL"
        ]),

        "won":
        len([
            x for x in leads
            if x.pipeline_stage == "WON"
        ]),

        "lost":
        len([
            x for x in leads
            if x.pipeline_stage == "LOST"
        ])
    }
