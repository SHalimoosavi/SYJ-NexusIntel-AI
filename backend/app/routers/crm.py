from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.crm import CRMStatsResponse, CRMRevenueResponse, CRMPipelineResponse

from app.core.dependencies import (
    get_current_user,
)

from app.services.crm_service import (
    get_crm_stats,
    get_revenue_metrics,
    get_pipeline_metrics,
)

router = APIRouter(
    prefix="/crm",
    tags=["CRM Analytics"],
)


@router.get("/stats", response_model=CRMStatsResponse)
def crm_stats(
    db: Session = Depends(get_db),
    current_user=Depends(
        get_current_user
    ),
):
    return get_crm_stats(
        db,
        current_user[
            "organization_id"
        ],
    )


@router.get("/revenue", response_model=CRMRevenueResponse)
def crm_revenue(
    db: Session = Depends(get_db),
    current_user=Depends(
        get_current_user
    ),
):
    return get_revenue_metrics(
        db,
        current_user[
            "organization_id"
        ],
    )


@router.get("/pipeline", response_model=CRMPipelineResponse)
def crm_pipeline(
    db: Session = Depends(get_db),
    current_user=Depends(
        get_current_user
    ),
):
    return get_pipeline_metrics(
        db,
        current_user[
            "organization_id"
        ],
    )
