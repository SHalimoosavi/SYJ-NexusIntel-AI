from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.models.lead import Lead
from app.models.lead_note import LeadNote

from app.core.tenant import (
    tenant_filter,
    validate_tenant_access,
)


def create_note(
    db: Session,
    note_data,
    organization_id: int,
):
    lead = (
        db.query(Lead)
        .filter(
            Lead.id == note_data.lead_id,
            Lead.organization_id == organization_id,
        )
        .first()
    )

    if not lead:
        raise HTTPException(
            status_code=404,
            detail="Lead not found",
        )

    note = LeadNote(
        lead_id=note_data.lead_id,
        note=note_data.note,
        note_type=note_data.note_type,
        organization_id=organization_id,
    )

    db.add(note)

    db.commit()

    db.refresh(note)

    return note


def get_lead_notes(
    db: Session,
    lead_id: int,
    organization_id: int,
):
    return (
        tenant_filter(
            db.query(LeadNote),
            LeadNote,
            organization_id,
        )
        .filter(
            LeadNote.lead_id == lead_id
        )
        .order_by(
            LeadNote.created_at.desc()
        )
        .all()
    )


def delete_note(
    db: Session,
    note_id: int,
    organization_id: int,
):
    note = (
        tenant_filter(
            db.query(LeadNote),
            LeadNote,
            organization_id,
        )
        .filter(
            LeadNote.id == note_id
        )
        .first()
    )

    validate_tenant_access(
        note,
        organization_id,
    )

    db.delete(note)

    db.commit()

    return True
