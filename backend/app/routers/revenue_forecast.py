from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.services.revenue_forecast_service import (
    calculate_forecast
)

router = APIRouter(
    prefix="/revenue-forecast",
    tags=["Revenue Forecast"]
)


@router.get("/dashboard")
def revenue_dashboard(
    db: Session = Depends(get_db)
):
    return calculate_forecast(db)
