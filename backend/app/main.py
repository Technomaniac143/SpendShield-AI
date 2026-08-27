from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy import text

from app.api import auth, evidence, ingestion, procurement, users
from app.core.config import get_settings
from app.core.database import engine
from app.integrations.blockchain import get_fabric_client

app = FastAPI(title="SpendShield AI")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in get_settings().cors_origins.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
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


@app.on_event("shutdown")
def shutdown() -> None:
    get_fabric_client().close()


@app.get("/health")
def health() -> dict[str, Any]:
    fabric_status = get_fabric_client().health_check()
    return {"status": "ok", "fabric": fabric_status}


@app.get("/health/ready")
def readiness() -> dict[str, Any]:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(status_code=503, detail="database is unavailable") from exc
    
    fabric_status = get_fabric_client().health_check()
    return {
        "status": "ready",
        "database": "connected",
        "fabric": fabric_status
    }
