from dotenv import load_dotenv
from pathlib import Path
import os
import logging
from fastapi import Request
from fastapi.responses import JSONResponse

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.database import Base
from app.database.database import engine

from app.models.audit_log import AuditLog

from app.models.user import User
from app.models.lead import Lead
from app.models.osint_report import OSINTReport
from app.models.agent_memory import AgentMemory
from app.models.activity import Activity
from app.models.lead_note import LeadNote

from app.models.organization import Organization
from app.models.subscription import Subscription
from app.models.role import Role
from app.models.permission import Permission
from app.models.feature_flag import FeatureFlag
from app.models.ai_usage import AIUsage
from app.models.invitation import Invitation

from app.database.database import SessionLocal

from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from app.core.rate_limit import (\n    RateLimitBackendUnavailable,\n    rate_limit_manager,\n    rate_limit_policy_for_path,\n)
from app.core.api_docs import api_docs_config

from app.services.role_service import (
    seed_roles,
)

from app.routers.auth import router as auth_router
from app.routers.leads import router as leads_router
from app.routers.osint import router as osint_router
from app.routers.intelligence import router as intelligence_router
from app.routers.technology import router as technology_router

from app.routers.organization_dashboard import (
    router as organization_dashboard_router
)

from app.routers.dashboard import (
    router as dashboard_router
)

from app.routers.audit import (
    router as audit_router
)

from app.routers.relationship_intelligence import (
    router as relationship_intelligence_router
)

from app.routers.agent_memory import (
    router as agent_memory_router
)

from app.routers.multi_agent import (
    router as multi_agent_router
)

from app.routers.sales_agent import (
    router as sales_agent_router
)

from app.routers.business_discovery import (
    router as business_discovery_router
)

from app.routers.executive_intelligence import (
    router as executive_intelligence_router
)

from app.routers.revenue_forecast import (
    router as revenue_forecast_router
)

from app.routers.crm import (
    router as crm_router
)

from app.routers.lead_qualification import (
    router as lead_qualification_router
)

from app.routers.report import (
    router as report_router
)

from app.routers.opportunity import (
    router as opportunity_router
)

from app.routers.activity import (
    router as activity_router
)

from app.routers.lead_note import (
    router as lead_note_router
)

from app.routers.organization import (
    router as organization_router
)

from app.routers.subscription import (
    router as subscription_router
)

from app.routers.invitation import (
    router as invitation_router
)

from app.routers.users import (
    router as users_router
)

Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    seed_roles(db)

finally:
    db.close()

app = FastAPI(
    title="SYJ NexusIntel AI",
    description="AI Powered Business Intelligence, Lead Discovery and OSINT Platform",
    version="1.0.0",
    **api_docs_config(),
)

app.add_middleware(
    ProxyHeadersMiddleware,
    trusted_hosts=os.getenv("TRUSTED_PROXY_HOSTS", "127.0.0.1").split(","),
)

CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "https://syj-nexus-intel-ai.vercel.app,http://localhost:3000",
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)

app.include_router(auth_router)
app.include_router(leads_router)
app.include_router(osint_router)
app.include_router(intelligence_router)
app.include_router(technology_router)

app.include_router(
    organization_dashboard_router
)

app.include_router(
    audit_router
)

app.include_router(
    dashboard_router
)

app.include_router(
    business_discovery_router
)

app.include_router(
    lead_qualification_router
)

app.include_router(
    report_router
)

app.include_router(
    opportunity_router
)

app.include_router(
    activity_router
)

app.include_router(
    relationship_intelligence_router
)

app.include_router(
    lead_note_router
)

app.include_router(
    organization_router
)

app.include_router(
    subscription_router
)

app.include_router(
    invitation_router
)

app.include_router(
    users_router
)

app.include_router(
    crm_router
)

app.include_router(
    revenue_forecast_router
)

app.include_router(
    executive_intelligence_router
)

app.include_router(
    sales_agent_router
)

app.include_router(
    multi_agent_router
)

app.include_router(
    agent_memory_router
)

@app.middleware("http")
async def apply_route_rate_limits(request: Request, call_next):
    client_ip = request.client.host if request.client else "unknown"
    path = request.url.path
    limit, window_seconds = rate_limit_policy_for_path(path)
    identity = f"ip:{client_ip}:{request.method}:{path}"
    try:
        allowed, retry_after = rate_limit_manager.check(
            identity,
            limit,
            window_seconds,
        )
    except RateLimitBackendUnavailable:
        return JSONResponse(
            status_code=503,
            content={"detail": "Rate limiting service unavailable"},
            headers={"Retry-After": "5"},
        )

    if not allowed:
        logging.getLogger("security.rate_limit").warning(
            "rate_limit_hit scope=ip method=%s route_group=%s",
            request.method,
            path.split("/", 2)[1] if path.count("/") >= 1 else "root",
        )
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded. Please retry later."},
            headers={"Retry-After": str(retry_after)},
        )
    return await call_next(request)

@app.get("/")
def root():
    return {
        "status": "online",
        "product": "SYJ NexusIntel AI",
        "version": "1.0.0",
    }


@app.get("/health")
def health():
    return {
        "success": True,
        "message": "Backend running successfully",
    }
