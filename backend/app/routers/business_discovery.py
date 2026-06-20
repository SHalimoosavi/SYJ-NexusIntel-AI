from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.schemas.business_discovery import (
    BusinessSearchRequest
)

from app.services.business_discovery_service import (
    search_businesses
)

router = APIRouter(
    prefix="/business-discovery",
    tags=["Business Discovery"]
)


@router.post("/search")
def discover_businesses(
    request: BusinessSearchRequest,
    db: Session = Depends(get_db)
):

    businesses = search_businesses(
        db,
        request.city,
        request.category
    )

    return {
        "count": len(businesses),
        "results": businesses
    }
