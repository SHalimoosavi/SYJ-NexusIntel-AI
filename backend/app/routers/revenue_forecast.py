from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.revenue_forecast import RevenueForecastResponse

from app.core.dependencies import (
    get_current_user,
)

from app.services.revenue_forecast_service import (
    calculate_forecast,
)

router = APIRouter(
    prefix="/revenue-forecast",
    tags=["Revenue Forecast"],
)


@router.get("/dashboard", response_model=RevenueForecastResponse)
def revenue_dashboard(
    db: Session = Depends(get_db),
    current_user=Depends(
        get_current_user
    ),
):
    return calculate_forecast(
        db,
        current_user[
            "organization_id"
        ],
    )
