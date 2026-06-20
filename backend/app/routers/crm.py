from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.services.crm_service import (
    get_crm_stats,
    get_revenue_metrics,
    get_pipeline_metrics
)

router = APIRouter(
    prefix="/crm",
    tags=["CRM Analytics"]
)


@router.get("/stats")
def crm_stats(
    db: Session = Depends(get_db)
):
    return get_crm_stats(db)


@router.get("/revenue")
def crm_revenue(
    db: Session = Depends(get_db)
):
    return get_revenue_metrics(db)


@router.get("/pipeline")
def crm_pipeline(
    db: Session = Depends(get_db)
):
    return get_pipeline_metrics(db)
