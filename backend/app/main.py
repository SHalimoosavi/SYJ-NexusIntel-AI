from fastapi import FastAPI

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

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SYJ NexusIntel AI",
    description="AI Powered Business Intelligence, Lead Discovery and OSINT Platform",
    version="1.0.0"
)

app.include_router(auth_router)
app.include_router(leads_router)
app.include_router(osint_router)
app.include_router(intelligence_router)
app.include_router(technology_router)


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
