from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.input_validation import validate_domain
from app.database.database import get_db
from app.schemas.agent_memory import AgentMemoryCreate, AgentMemoryResponse
from app.services.agent_memory_service import save_memory, get_history, get_latest

router = APIRouter(prefix="/agent-memory", tags=["Agent Memory"])


@router.post("/save", response_model=AgentMemoryResponse)
def create_memory(
    payload: AgentMemoryCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return save_memory(
        db,
        payload.model_dump(),
        current_user["organization_id"],
    )


@router.get("/history/{domain}", response_model=list[AgentMemoryResponse])
def history(
    domain: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_history(db, validate_domain(domain), current_user["organization_id"])


@router.get("/latest/{domain}", response_model=AgentMemoryResponse | None)
def latest(
    domain: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_latest(db, validate_domain(domain), current_user["organization_id"])
