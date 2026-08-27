from fastapi import APIRouter, Depends, HTTPException
from typing import Any
import uuid
from app.agents.audit_agent import AuditAgent
from app.core.security import get_current_user_context

router = APIRouter()

@router.post("/")
async def start_investigation(
    supplier_id: str,
    invoice_id: str = None,
    context: dict = Depends(get_current_user_context)
) -> Any:
    """
    Triggers an AuditAgent investigation.
    """
    agent = AuditAgent(tenant_id=str(context["tenant_id"]))
    result = await agent.investigate_supplier(supplier_id=supplier_id, invoice_id=invoice_id)
    
    # In a full setup, this would save an Investigation and Recommendation to the DB
    return {
        "status": "COMPLETED",
        "data": result
    }
