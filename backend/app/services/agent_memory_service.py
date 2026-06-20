import json

from sqlalchemy.orm import Session

from app.models.agent_memory import (
    AgentMemory
)


def save_memory(
    db: Session,
    data: dict
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
    domain: str
):

    return (
        db.query(
            AgentMemory
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
    domain: str
):

    return (
        db.query(
            AgentMemory
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
