from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.schemas.lead_note import LeadNoteCreate, LeadNoteResponse
from app.schemas.common import SuccessResponse

from app.services.lead_note_service import (
    create_note,
    get_lead_notes,
    delete_note,
)

from app.core.dependencies import (
    get_current_user,
)

router = APIRouter(
    prefix="/lead-notes",
    tags=["Lead Notes"],
)


@router.post(
    "",
    response_model=LeadNoteResponse,
)
def create_note_route(
    note: LeadNoteCreate,
    db: Session = Depends(get_db),
    current_user=Depends(
        get_current_user
    ),
):
    return create_note(
        db,
        note,
        current_user["organization_id"],
        current_user["user_id"],
    )


@router.get(
    "/{lead_id}",
    response_model=list[LeadNoteResponse],
)
def get_notes_route(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        get_current_user
    ),
):
    return get_lead_notes(
        db,
        lead_id,
        current_user["organization_id"],
    )


@router.delete(
    "/{note_id}",
    response_model=SuccessResponse,
)
def delete_note_route(
    note_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        get_current_user
    ),
):
    success = delete_note(
        db,
        note_id,
        current_user["organization_id"],
    )

    return {
        "success": success,
    }
