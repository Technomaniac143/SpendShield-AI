from typing import Any
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy import text

from app.api import auth, evidence, ingestion, procurement, users, market
from app.core.config import get_settings
from app.core.database import engine
from app.integrations.blockchain import get_fabric_client

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    settings = get_settings()
    if settings.evidence_ledger_backend == "blockchain":
        get_fabric_client().close()


app = FastAPI(title="SpendShield AI", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in get_settings().cors_origins.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "PUT", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Idempotency-Key"],
)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    return response
app.include_router(evidence.router, prefix="/api/v1")
app.include_router(procurement.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(ingestion.router, prefix="/api/v1")
app.include_router(market.router, prefix="/api/v1")


@app.get("/health")
def health() -> dict[str, Any]:
    settings = get_settings()
    if settings.evidence_ledger_backend == "database":
        fabric_status = {"status": "disabled", "channel": settings.fabric_channel, "chaincode": settings.fabric_chaincode}
    else:
        fabric_status = get_fabric_client().health_check()
        
    market_status = {
        "enabled": settings.market_intelligence_enabled,
        "mode": settings.market_intelligence_mode,
        "database": "healthy"
    }
    return {
        "status": "ok", 
        "fabric": fabric_status,
        "market_intelligence": market_status
    }


@app.get("/health/ready")
def readiness() -> dict[str, Any]:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(status_code=503, detail="database is unavailable") from exc
    
    settings = get_settings()
    if settings.evidence_ledger_backend == "database":
        fabric_status = {"status": "disabled", "channel": settings.fabric_channel, "chaincode": settings.fabric_chaincode}
    else:
        fabric_status = get_fabric_client().health_check()
        
    market_status = {
        "enabled": settings.market_intelligence_enabled,
        "mode": settings.market_intelligence_mode,
        "database": "healthy"
    }
    return {
        "status": "ready",
        "database": "connected",
        "fabric": fabric_status,
        "market_intelligence": market_status
    }
