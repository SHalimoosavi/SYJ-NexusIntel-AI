from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.relationship_intelligence import RelationshipIntelligenceResponse

from app.core.dependencies import (
    get_current_user,
)

from app.services.relationship_intelligence import (
    get_relationship_intelligence,
)

router = APIRouter(
    prefix="/relationship-intelligence",
    tags=["Relationship Intelligence"],
)


@router.get("", response_model=RelationshipIntelligenceResponse)
def relationship_dashboard(
    db: Session = Depends(get_db),
    current_user=Depends(
        get_current_user
    ),
):
    return get_relationship_intelligence(
        db,
        current_user[
            "organization_id"
        ],
    )
