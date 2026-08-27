from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import Principal, require_permission
from app.core.config import get_settings
from app.core.database import get_db
from app.integrations.blockchain import FabricClient, FabricUnavailable, get_fabric_client
from app.integrations.storage import ObjectStorage, create_storage
from app.models import Evidence
from app.schemas import RegisterEvidenceRequest
from app.services.evidence import EvidenceService
from app.utils import deterministic_modified_hash

router = APIRouter(prefix="/evidence", tags=["evidence"])
MAX_DOCUMENT_BYTES = get_settings().max_document_bytes


async def read_pdf(document: UploadFile) -> bytes:
    if document.content_type not in (None, "application/pdf"):
        raise HTTPException(status_code=422, detail="document must be a PDF")

    chunks: list[bytes] = []
    total = 0
    while chunk := await document.read(1024 * 1024):
        total += len(chunk)
        if total > MAX_DOCUMENT_BYTES:
            raise HTTPException(status_code=413, detail="document is too large")
        chunks.append(chunk)

    content = b"".join(chunks)
    if not content.startswith(b"%PDF-"):
        raise HTTPException(status_code=422, detail="invalid PDF document")
    return content


def get_storage() -> ObjectStorage:
    return create_storage()


def service(db: Session = Depends(get_db), fabric: FabricClient = Depends(get_fabric_client),
            storage: ObjectStorage = Depends(get_storage)) -> EvidenceService:
    return EvidenceService(db, fabric, storage)


@router.post("/{event_id}/register")
async def register(event_id: str, record_id: str = Form(...), event_type: str = Form(...), timestamp: str = Form(...),
             source_type: str = Form("DOCUMENT"), source_id: str | None = Form(None), metadata_hash: str | None = Form(None),
             document: UploadFile = File(...), principal: Principal = Depends(require_permission("evidence:write")),
             evidence_service: EvidenceService = Depends(service)):
    try:
        content = await read_pdf(document)
        request = RegisterEvidenceRequest(record_id=record_id, event_type=event_type, timestamp=timestamp,
                                          source_type=source_type, source_id=source_id, metadata_hash=metadata_hash)
        return evidence_service.register(event_id, request, principal, content)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/{event_id}")
def get_evidence(event_id: str, principal: Principal = Depends(require_permission("evidence:read")), db: Session = Depends(get_db)):
    record = db.scalar(select(Evidence).where(Evidence.fabric_event_id == event_id, Evidence.tenant_id == principal.tenant_id))
    if record is None:
        return {"status": "NOT_REGISTERED", "eventId": event_id}
    return EvidenceService.to_response(record, "FOUND")


@router.post("/{event_id}/verify")
def verify(event_id: str, principal: Principal = Depends(require_permission("evidence:verify")),
          evidence_service: EvidenceService = Depends(service)):
    try:
        return evidence_service.verify(event_id, principal)
    except (ValueError, FabricUnavailable) as exc:
        raise HTTPException(status_code=503 if isinstance(exc, FabricUnavailable) else 422, detail=str(exc)) from exc


@router.get("/{event_id}/history")
def history(event_id: str, principal: Principal = Depends(require_permission("evidence:read")), db: Session = Depends(get_db),
           fabric: FabricClient = Depends(get_fabric_client)):
    owner = db.scalar(select(Evidence).where(Evidence.fabric_event_id == event_id, Evidence.tenant_id == principal.tenant_id))
    if owner is None:
        return {"status": "NOT_REGISTERED", "eventId": event_id}
    try:
        return fabric.get_history(event_id) | {"tenantId": principal.tenant_id}
    except FabricUnavailable as exc:
        raise HTTPException(status_code=503, detail="Fabric is unavailable") from exc


@router.post("/{event_id}/simulate-modification")
def simulate_modification(event_id: str, principal: Principal = Depends(require_permission("evidence:verify")), db: Session = Depends(get_db)):
    record = db.scalar(select(Evidence).where(Evidence.fabric_event_id == event_id, Evidence.tenant_id == principal.tenant_id))
    if record is None:
        return {"status": "NOT_REGISTERED", "eventId": event_id}
    modified = deterministic_modified_hash(record.document_hash)
    return {"status": "INTEGRITY_FAILURE", "registered_hash": record.document_hash, "simulated_current_hash": modified}


@router.get("/{event_id}/blockchain")
def blockchain(event_id: str, principal: Principal = Depends(require_permission("evidence:read")), db: Session = Depends(get_db),
               fabric: FabricClient = Depends(get_fabric_client)):
    record = db.scalar(select(Evidence).where(Evidence.fabric_event_id == event_id, Evidence.tenant_id == principal.tenant_id))
    if record is None:
        return {"status": "NOT_REGISTERED", "eventId": event_id}
    if not record.fabric_transaction_id:
        return {"status": record.verification_status, "eventId": event_id, "fabric": None}
    try:
        metadata = fabric.get_transaction(record.fabric_transaction_id)
    except FabricUnavailable as exc:
        raise HTTPException(status_code=503, detail="Fabric is unavailable") from exc
    record.fabric_block_number = metadata["blockNumber"]
    record.fabric_block_hash = metadata["blockHash"]
    db.commit()
    return {"evidence_id": record.evidence_id, "record_id": record.record_id, "verification_status": record.verification_status,
            "fabric": {"channel": metadata["channel"], "chaincode": metadata["chaincode"],
                       "transaction_id": metadata["transactionId"], "block_number": metadata["blockNumber"],
                       "block_hash": metadata["blockHash"], "timestamp": metadata.get("timestamp"),
                       "validation_status": metadata.get("validationCode")}}
