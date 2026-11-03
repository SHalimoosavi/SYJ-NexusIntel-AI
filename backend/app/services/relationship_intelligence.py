from datetime import datetime

from app.core.clock import utcnow_naive

from sqlalchemy.orm import Session

from app.models.lead import Lead

from app.core.tenant import tenant_filter


def get_relationship_intelligence(
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

    total = len(leads)

    overdue = 0
    healthy = 0

    engagement_score = 0

    recommendations = []

    today = utcnow_naive()

    for lead in leads:
        score = lead.lead_score or 0

        engagement_score += score

        if lead.next_followup:
            try:
                followup_date = datetime.fromisoformat(
                    lead.next_followup
                )

                if followup_date < today:
                    overdue += 1

            except Exception:
                pass

        if score >= 70:
            healthy += 1

    avg_engagement = 0

    if total > 0:
        avg_engagement = int(
            engagement_score / total
        )

    if overdue > 0:
        recommendations.append(
            f"{overdue} overdue followups require attention"
        )

    if healthy < total:
        recommendations.append(
            "Increase engagement on WARM leads"
        )

    return {
        "total_leads": total,
        "healthy_relationships": healthy,
        "overdue_followups": overdue,
        "engagement_score": avg_engagement,
        "recommendations": recommendations,
    }
