from fastapi import APIRouter, Depends, HTTPException
from typing import Any
from pydantic import BaseModel
import uuid
from app.core.security import get_current_user_context

router = APIRouter()

class DecisionRequest(BaseModel):
    decision: str # ACCEPTED, REJECTED, OVERRIDDEN
    reason: str = None

@router.post("/{recommendation_id}/decision")
async def make_decision(
    recommendation_id: uuid.UUID,
    decision_req: DecisionRequest,
    context: dict = Depends(get_current_user_context)
) -> Any:
    """
    Human-in-the-loop decision endpoint for a specific recommendation.
    """
    # In a real implementation, this would:
    # 1. Fetch the Recommendation from DB
    # 2. Verify it belongs to the tenant
    # 3. Create a Decision record
    # 4. Trigger Outcome generation
    
    if decision_req.decision not in ["ACCEPTED", "REJECTED", "OVERRIDDEN"]:
        raise HTTPException(status_code=400, detail="Invalid decision type")
        
    if decision_req.decision == "OVERRIDDEN" and not decision_req.reason:
        raise HTTPException(status_code=400, detail="Reason is required for OVERRIDDEN decisions")
        
    return {
        "status": "SUCCESS",
        "message": f"Decision {decision_req.decision} recorded for recommendation {recommendation_id}",
        "user_id": context["user_id"]
    }
