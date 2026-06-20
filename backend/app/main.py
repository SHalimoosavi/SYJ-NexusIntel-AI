from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.database import Base
from app.database.database import engine

from app.models.user import User
from app.models.lead import Lead
from app.models.osint_report import OSINTReport

from app.routers.auth import router as auth_router
from app.routers.leads import router as leads_router
from app.routers.osint import router as osint_router
from app.routers.intelligence import router as intelligence_router
from app.routers.technology import router as technology_router
from app.routers.business_discovery import (
    router as business_discovery_router
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

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SYJ NexusIntel AI",
    description="AI Powered Business Intelligence, Lead Discovery and OSINT Platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(leads_router)
app.include_router(osint_router)
app.include_router(intelligence_router)
app.include_router(technology_router)
app.include_router(business_discovery_router)
app.include_router(lead_qualification_router)
app.include_router(report_router)
app.include_router(opportunity_router)


@app.get("/")
def root():
    return {
        "status": "online",
        "product": "SYJ NexusIntel AI",
        "version": "1.0.0"
    }


@app.get("/health")
def health():
    return {
        "success": True,
        "message": "Backend running successfully"
    }
