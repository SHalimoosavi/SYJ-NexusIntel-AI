from fastapi import APIRouter

from app.schemas.osint import DomainRequest

from app.services.osint_service import get_dns
from app.services.osint_service import get_ip
from app.services.osint_service import get_seo_data
from app.services.osint_service import get_security_headers
from app.services.osint_service import get_ssl_info
from app.services.osint_service import get_whois

router = APIRouter(
    prefix="/osint",
    tags=["OSINT"]
)


@router.post("/domain")
def analyze_domain(
    request: DomainRequest
):
    domain = request.domain

    return {
        "domain": domain,
        "ip": get_ip(domain),
        "whois": get_whois(domain),
        "dns": get_dns(domain),
        "ssl": get_ssl_info(domain),
        "security_headers":
            get_security_headers(domain),
        "seo":
            get_seo_data(domain)
    }
