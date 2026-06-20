from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.services.executive_intelligence_service import (
    generate_executive_briefing,
    get_top_opportunities,
    get_risks
)

router = APIRouter(
    prefix="/executive-intelligence",
    tags=["Executive Intelligence"]
)


@router.get("/briefing")
def executive_briefing(
    db: Session = Depends(get_db)
):
    return generate_executive_briefing(
        db
    )


@router.get("/opportunities")
def opportunities(
    db: Session = Depends(get_db)
):
    return get_top_opportunities(
        db
    )


@router.get("/risks")
def risks(
    db: Session = Depends(get_db)
):
    return get_risks(db)
