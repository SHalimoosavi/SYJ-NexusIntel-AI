from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.database import (
    get_db,
)

from app.core.dependencies import (
    get_current_user,
)

from app.services.agent_memory_service import (
    save_memory,
    get_history,
    get_latest,
)

router = APIRouter(
    prefix="/agent-memory",
    tags=["Agent Memory"],
)


@router.post("/save")
def create_memory(
    payload: dict,
    db: Session = Depends(get_db),
    current_user=Depends(
        get_current_user
    ),
):
    return save_memory(
        db,
        payload,
        current_user[
            "organization_id"
        ],
    )


@router.get("/history/{domain}")
def history(
    domain: str,
    db: Session = Depends(get_db),
    current_user=Depends(
        get_current_user
    ),
):
    return get_history(
        db,
        domain,
        current_user[
            "organization_id"
        ],
    )


@router.get("/latest/{domain}")
def latest(
    domain: str,
    db: Session = Depends(get_db),
    current_user=Depends(
        get_current_user
    ),
):
    return get_latest(
        db,
        domain,
        current_user[
            "organization_id"
        ],
    )
