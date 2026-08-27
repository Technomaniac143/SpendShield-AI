from fastapi import FastAPI

from app.api import evidence
from app.integrations.blockchain import get_fabric_client

app = FastAPI(title="SpendShield AI")
app.include_router(evidence.router, prefix="/api/v1")


@app.on_event("shutdown")
def shutdown() -> None:
    get_fabric_client().close()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
