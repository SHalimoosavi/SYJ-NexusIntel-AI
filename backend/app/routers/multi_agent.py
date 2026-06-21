from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.schemas.multi_agent import (
    MultiAgentRequest,
)

from app.services.multi_agent_service import (
    run_multi_agent_analysis,
)

from app.services.ai_usage_service import (
    enforce_ai_limit,
    log_ai_request,
)

from app.core.dependencies import (
    get_current_user,
)

from app.core.feature_guard import (
    require_feature,
)

from app.core.feature_constants import (
    MULTI_AGENT,
)

router = APIRouter(
    prefix="/multi-agent",
    tags=["Multi Agent"],
)


@router.post("/analyze")
def analyze(
    request: MultiAgentRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_feature(
            MULTI_AGENT
        )
    ),
):
    organization_id = current_user[
        "organization_id"
    ]

    enforce_ai_limit(
        db,
        organization_id,
    )

    result = run_multi_agent_analysis(
        request.domain,
        db,
        organization_id,
    )

    log_ai_request(
        db,
        organization_id,
        "MULTI_AGENT",
    )

    return result
