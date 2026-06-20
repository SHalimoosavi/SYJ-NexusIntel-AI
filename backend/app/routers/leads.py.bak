from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.schemas.lead import LeadCreate

from app.services.lead_service import create_lead
from app.services.lead_service import get_all_leads
from app.services.lead_service import delete_lead

router = APIRouter(
    prefix="/leads",
    tags=["Lead Management"]
)


@router.post("/")
def add_lead(
    lead: LeadCreate,
    db: Session = Depends(get_db)
):
    return create_lead(
        db,
        lead
    )


@router.get("/")
def list_leads(
    db: Session = Depends(get_db)
):
    return get_all_leads(db)


@router.delete("/{lead_id}")
def remove_lead(
    lead_id: int,
    db: Session = Depends(get_db)
):

    deleted = delete_lead(
        db,
        lead_id
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Lead not found"
        )

    return {
        "success": True
    }
