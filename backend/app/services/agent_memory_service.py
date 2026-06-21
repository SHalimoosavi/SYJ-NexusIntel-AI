import json

from sqlalchemy.orm import Session

from app.models.agent_memory import AgentMemory

from app.core.tenant import (
    tenant_filter,
)


def save_memory(
    db: Session,
    data: dict,
    organization_id: int,
):
    memory = AgentMemory(
        domain=data.get(
            "domain"
        ),

        overall_score=data.get(
            "overall_score",
            0
        ),

        priority=data.get(
            "priority",
            "UNKNOWN"
        ),

        estimated_value=data.get(
            "estimated_value",
            ""
        ),

        organization_id=
        organization_id,

        analysis_data=json.dumps(
            data
        )
    )

    db.add(memory)

    db.commit()

    db.refresh(memory)

    return memory


def get_history(
    db: Session,
    domain: str,
    organization_id: int,
):
    return (
        tenant_filter(
            db.query(
                AgentMemory
            ),
            AgentMemory,
            organization_id,
        )
        .filter(
            AgentMemory.domain
            == domain
        )
        .order_by(
            AgentMemory.created_at.desc()
        )
        .all()
    )


def get_latest(
    db: Session,
    domain: str,
    organization_id: int,
):
    return (
        tenant_filter(
            db.query(
                AgentMemory
            ),
            AgentMemory,
            organization_id,
        )
        .filter(
            AgentMemory.domain
            == domain
        )
        .order_by(
            AgentMemory.created_at.desc()
        )
        .first()
    )
