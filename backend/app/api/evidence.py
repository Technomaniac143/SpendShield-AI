from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.integrations.blockchain import FabricClient, FabricUnavailable
from app.models import Evidence
from app.schemas import RegisterEvidenceRequest, VerifyEvidenceRequest
from app.services.evidence import EvidenceService
from app.utils import deterministic_modified_hash

router = APIRouter(prefix="/evidence", tags=["evidence"])


def service(db: Session = Depends(get_db)) -> EvidenceService:
    return EvidenceService(db, FabricClient())


@router.post("/{event_id}/register")
def register(event_id: str, request: RegisterEvidenceRequest, evidence_service: EvidenceService = Depends(service)):
    try:
        return evidence_service.register(event_id, request)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/{event_id}")
def get_evidence(event_id: str, tenant_id: str, db: Session = Depends(get_db)):
    record = db.scalar(select(Evidence).where(Evidence.fabric_event_id == event_id, Evidence.tenant_id == tenant_id))
    if record is None:
        return {"status": "NOT_REGISTERED", "eventId": event_id}
    return EvidenceService.to_response(record, "FOUND")


@router.post("/{event_id}/verify")
def verify(event_id: str, request: VerifyEvidenceRequest, evidence_service: EvidenceService = Depends(service)):
    try:
        return evidence_service.verify(event_id, request.tenant_id, request.current_document_hash)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/{event_id}/history")
def history(event_id: str, tenant_id: str, db: Session = Depends(get_db), fabric: FabricClient = Depends(FabricClient)):
    owner = db.scalar(select(Evidence).where(Evidence.fabric_event_id == event_id, Evidence.tenant_id == tenant_id))
    if owner is None:
        return {"status": "NOT_REGISTERED", "eventId": event_id}
    return fabric.get_history(event_id) | {"eventId": event_id, "tenantId": tenant_id}


@router.post("/{event_id}/simulate-modification")
def simulate_modification(event_id: str, tenant_id: str, db: Session = Depends(get_db)):
    record = db.scalar(select(Evidence).where(Evidence.fabric_event_id == event_id, Evidence.tenant_id == tenant_id))
    if record is None:
        return {"status": "NOT_REGISTERED", "eventId": event_id}
    modified = deterministic_modified_hash(record.document_hash)
    return {"status": "INTEGRITY_FAILURE", "registered_hash": record.document_hash, "simulated_current_hash": modified}


@router.get("/{event_id}/blockchain")
def blockchain(event_id: str, tenant_id: str, db: Session = Depends(get_db), fabric: FabricClient = Depends(FabricClient)):
    record = db.scalar(select(Evidence).where(Evidence.fabric_event_id == event_id, Evidence.tenant_id == tenant_id))
    if record is None:
        return {"status": "NOT_REGISTERED", "eventId": event_id}
    try:
        metadata = fabric.get_transaction(record.fabric_transaction_id) if record.fabric_transaction_id else {}
    except FabricUnavailable:
        metadata = {}
    return {"evidence_id": record.evidence_id, "record_id": record.record_id, "verification_status": record.verification_status,
            "fabric": {"channel": record.fabric_channel, "chaincode": record.fabric_chaincode,
                       "transaction_id": record.fabric_transaction_id, "block_number": metadata.get("blockNumber"),
                       "block_hash": metadata.get("blockHash"), "timestamp": metadata.get("timestamp"),
                       "validation_status": metadata.get("validationCode")}}
