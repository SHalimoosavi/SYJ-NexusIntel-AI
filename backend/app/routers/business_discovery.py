from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.schemas.business_discovery import (
    BusinessSearchRequest,
)

from app.services.business_discovery_service import (
    search_businesses,
)

from app.core.dependencies import (
    get_current_user,
)

router = APIRouter(
    prefix="/business-discovery",
    tags=["Business Discovery"],
)


@router.post("/search")
def discover_businesses(
    request: BusinessSearchRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        get_current_user
    ),
):
    businesses = search_businesses(
        db,
        request.city,
        request.category,
        current_user[
            "organization_id"
        ],
    )

    return {
        "count": len(
            businesses
        ),
        "results": businesses,
    }
