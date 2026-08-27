from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def health_check():
    return {"status": "ok"}

@router.get("/ready")
def readiness_check():
    # TODO: Add DB/Redis checks
    return {"status": "ready"}
