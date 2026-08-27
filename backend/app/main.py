from fastapi import FastAPI

from app.api import evidence
from app.core.database import Base, engine

Base.metadata.create_all(bind=engine)
app = FastAPI(title="SpendShield AI")
app.include_router(evidence.router, prefix="/api/v1")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
