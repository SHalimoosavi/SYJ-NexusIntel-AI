from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.schemas.osint import DomainRequest, OSINTAnalysisResponse

from app.services.osint_service import (
    get_dns,
    get_ip,
    get_seo_data,
    get_security_headers,
    get_ssl_info,
    get_whois,
)

from app.services.ai_usage_service import (
    enforce_ai_limit,
    log_ai_request,
)

from app.core.dependencies import (
    get_current_user,
)

router = APIRouter(
    prefix="/osint",
    tags=["OSINT"],
)


@router.post("/domain", response_model=OSINTAnalysisResponse)
def analyze_domain(
    request: DomainRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        get_current_user
    ),
):
    organization_id = current_user[
        "organization_id"
    ]

    enforce_ai_limit(
        db,
        organization_id,
    )

    domain = request.domain

    result = {
        "domain": domain,
        "ip": get_ip(domain),
        "whois": get_whois(domain),
        "dns": get_dns(domain),
        "ssl": get_ssl_info(domain),
        "security_headers":
            get_security_headers(domain),
        "seo":
            get_seo_data(domain),
    }

    log_ai_request(
        db,
        organization_id,
        "OSINT_SCAN",
    )

    return result
