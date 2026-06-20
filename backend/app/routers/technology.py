from fastapi import APIRouter

from app.schemas.technology import (
    TechnologyRequest
)

from app.services.technology_service import (
    detect_technologies
)

router = APIRouter(
    prefix="/technology",
    tags=["Technology Detection"]
)


@router.post("/detect")
def technology_detection(
    request: TechnologyRequest
):

    return detect_technologies(
        request.domain
    )
