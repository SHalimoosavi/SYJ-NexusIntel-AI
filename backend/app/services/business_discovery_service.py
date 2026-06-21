from sqlalchemy.orm import Session

from app.models.lead import Lead

from app.core.tenant import tenant_filter


def search_businesses(
    db: Session,
    city: str,
    category: str,
    organization_id: int,
):
    query = tenant_filter(
        db.query(Lead),
        Lead,
        organization_id,
    )

    if city:
        query = query.filter(
            Lead.city.ilike(
                f"%{city}%"
            )
        )

    if category:
        query = query.filter(
            Lead.category.ilike(
                f"%{category}%"
            )
        )

    return query.all()
