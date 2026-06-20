from sqlalchemy.orm import Session

from app.models.lead import Lead


def search_businesses(
    db: Session,
    city: str,
    category: str
):

    query = db.query(Lead)

    if city:
        query = query.filter(
            Lead.city.ilike(f"%{city}%")
        )

    if category:
        query = query.filter(
            Lead.category.ilike(
                f"%{category}%"
            )
        )

    return query.all()
