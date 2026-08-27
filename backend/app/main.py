from fastapi import FastAPI
from app.api.v1 import health, auth, investigations, recommendations

app = FastAPI(
    title="SpendShield AI",
    description="AI Procurement Investigation & Outcome Intelligence Platform",
    version="1.0.0"
)

app.include_router(health.router, prefix="/api/v1/health", tags=["health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(investigations.router, prefix="/api/v1/investigations", tags=["investigations"])
app.include_router(recommendations.router, prefix="/api/v1/recommendations", tags=["recommendations"])

@app.get("/")
def read_root():
    return {"message": "Welcome to SpendShield AI Backend"}
