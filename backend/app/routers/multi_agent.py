from fastapi import APIRouter

from app.schemas.multi_agent import (
    MultiAgentRequest
)

from app.services.multi_agent_service import (
    run_multi_agent_analysis
)

router = APIRouter(
    prefix="/multi-agent",
    tags=["Multi Agent"]
)


@router.post("/analyze")
def analyze(
    request: MultiAgentRequest
):

    return run_multi_agent_analysis(
        request.domain
    )
