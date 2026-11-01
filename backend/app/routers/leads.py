from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.schemas.lead import LeadCreate, LeadUpdate, LeadResponse
from app.schemas.common import SuccessResponse

from app.services.lead_service import (
    create_lead,
    get_all_leads,
    update_lead_pipeline,
    delete_lead,
)

from app.core.dependencies import (
    get_current_user,
)

router = APIRouter(
    prefix="/leads",
    tags=["Lead Management"],
)


@router.post("", response_model=LeadResponse)
def add_lead(
    lead: LeadCreate,
    db: Session = Depends(get_db),
    current_user=Depends(
        get_current_user
    ),
):
    return create_lead(
        db,
        lead,
        current_user["organization_id"],
        current_user["user_id"],
    )


@router.get("", response_model=list[LeadResponse])
def list_leads(
    db: Session = Depends(get_db),
    current_user=Depends(
        get_current_user
    ),
):
    return get_all_leads(
        db,
        current_user[
            "organization_id"
        ],
    )


@router.put("/{lead_id}", response_model=LeadResponse)
def update_pipeline(
    lead_id: int,
    data: LeadUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(
        get_current_user
    ),
):
    lead = update_lead_pipeline(
        db,
        lead_id,
        data,
        current_user["organization_id"],
        current_user["user_id"],
    )

    if not lead:
        raise HTTPException(
            status_code=404,
            detail="Lead not found",
        )

    return lead


@router.delete("/{lead_id}", response_model=SuccessResponse)
def remove_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        get_current_user
    ),
):
    deleted = delete_lead(
        db,
        lead_id,
        current_user["organization_id"],
        current_user["user_id"],
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Lead not found",
        )

    return {
        "success": True
    }
