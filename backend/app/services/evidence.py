import json
import logging
from typing import Any
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.auth import Principal
from app.core.config import get_settings
from app.integrations.blockchain import FabricClient
from app.integrations.storage import ObjectStorage, document_hash
from app.models import Evidence, FabricOutbox, OutboxStatus
from app.schemas import RegisterEvidenceRequest
from app.utils import is_sha256

logger = logging.getLogger(__name__)

SUPPORTED_EVENT_TYPES = {
    "INVOICE_REGISTERED", "GRN_REGISTERED", "PAYMENT_APPROVED", "PAYMENT_BLOCKED",
    "DISPUTE_CREATED", "DOCUMENT_VERIFIED", "DOCUMENT_INTEGRITY_FAILED",
    "RECOMMENDATION_ACCEPTED", "RECOMMENDATION_REJECTED", "OUTCOME_RECORDED",
}


class EvidenceService:
    def __init__(self, db: Session, fabric: FabricClient, storage: ObjectStorage):
        self.db = db
        self.fabric = fabric
        self.storage = storage
        self.settings = get_settings()

    def register(self, event_id: str, request: RegisterEvidenceRequest, principal: Principal, document: bytes) -> dict[str, Any]:
        if not document:
            raise ValueError("document is required")
        if request.event_type not in SUPPORTED_EVENT_TYPES:
            raise ValueError("unsupported event_type")
        content_hash = document_hash(document)
        metadata_hash = request.metadata_hash or document_hash(
            json.dumps({"record_id": request.record_id, "event_type": request.event_type}, sort_keys=True).encode()
        )
        if not is_sha256(metadata_hash):
            raise ValueError("metadata_hash must be a SHA-256 hexadecimal value")

        if self.settings.evidence_ledger_backend == "database":
            from app.services.evidence_ledger import EvidenceLedgerService
            ledger = EvidenceLedgerService(self.db)
            storage_key = f"{principal.tenant_id}/{event_id}/{uuid4().hex}.pdf"
            self.storage.put(storage_key, document)
            payload = {
                "eventId": event_id,
                "tenantId": principal.tenant_id,
                "recordId": request.record_id,
                "eventType": request.event_type,
                "documentHash": content_hash,
                "actor": principal.actor,
                "timestamp": request.timestamp,
                "metadataHash": metadata_hash,
                "storageKey": storage_key
            }
            try:
                res = ledger.register(payload)
                return {"status": "REGISTERED", "eventId": event_id, "transactionId": res["transactionId"]}
            except ValueError as exc:
                self._cleanup_object(storage_key)
                raise
            except Exception:
                self._cleanup_object(storage_key)
                raise

        existing = self.db.scalar(select(Evidence).where(Evidence.fabric_event_id == event_id))
        if existing:
            if existing.tenant_id != principal.tenant_id:
                raise ValueError("event_id is already registered")
            return self.to_response(existing, "ALREADY_REGISTERED")
        storage_key = f"{principal.tenant_id}/{event_id}/{uuid4().hex}.pdf"
        self.storage.put(storage_key, document)
        payload = {
            "eventId": event_id, "tenantId": principal.tenant_id, "recordId": request.record_id,
            "eventType": request.event_type, "documentHash": content_hash, "actor": principal.actor,
            "timestamp": request.timestamp, "metadataHash": metadata_hash.lower(),
        }
        record = Evidence(
            tenant_id=principal.tenant_id, source_type=request.source_type, source_id=request.source_id,
            storage_key=storage_key, record_id=request.record_id, event_type=request.event_type,
            document_hash=content_hash, metadata_hash=metadata_hash.lower(), created_by=principal.actor,
            event_timestamp=request.timestamp, fabric_event_id=event_id,
            fabric_channel=self.settings.fabric_channel, fabric_chaincode=self.settings.fabric_chaincode,
            verification_status="PENDING_BLOCKCHAIN_VERIFICATION",
        )
        outbox = FabricOutbox(tenant_id=principal.tenant_id, event_id=event_id, event_type=request.event_type,
                              payload=json.dumps(payload, sort_keys=True), status=OutboxStatus.PENDING)
        try:
            self.db.add_all([record, outbox])
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            self._cleanup_object(storage_key)
            raise ValueError("event_id is already registered") from exc
        except Exception:
            self.db.rollback()
            self._cleanup_object(storage_key)
            raise
        return {"status": "PENDING_BLOCKCHAIN_VERIFICATION", "eventId": event_id}

    def _cleanup_object(self, storage_key: str) -> None:
        try:
            self.storage.delete(storage_key)
        except Exception:
            logger.exception("failed to clean up evidence object", extra={"storage_key": storage_key})

    def verify(self, event_id: str, principal: Principal) -> dict[str, Any]:
        record = self.db.scalar(select(Evidence).where(Evidence.fabric_event_id == event_id, Evidence.tenant_id == principal.tenant_id))
        if record is None:
            return {"status": "NOT_REGISTERED", "eventId": event_id}
        current_hash = self.storage.hash(record.storage_key)

        if self.settings.evidence_ledger_backend == "database":
            from app.services.evidence_ledger import EvidenceLedgerService
            ledger = EvidenceLedgerService(self.db)
            res = ledger.verify_evidence(event_id, current_hash, principal.tenant_id)
            if res.get("status") == "VERIFIED":
                record.verification_status = "VERIFIED"
                self.db.commit()
            elif res.get("status") in ("TAMPERED", "INTEGRITY_FAILURE"):
                record.verification_status = "INTEGRITY_FAILURE"
                self.db.commit()
            return res

        registered = self.fabric.get_evidence(event_id)
        if registered.get("status") != "FOUND":
            return {"status": "PENDING_BLOCKCHAIN_VERIFICATION", "eventId": event_id}
        registered_hash = registered["documentHash"]
        status = "VERIFIED" if registered_hash == current_hash else "INTEGRITY_FAILURE"
        record.verification_status = status
        self.db.commit()
        return {"status": status, "eventId": event_id, "registeredHash": registered_hash, "currentHash": current_hash}

    @staticmethod
    def to_response(record: Evidence, status: str) -> dict[str, Any]:
        return {"status": status, "eventId": record.fabric_event_id, "tenantId": record.tenant_id,
                "recordId": record.record_id, "eventType": record.event_type, "documentHash": record.document_hash,
                "actor": record.created_by, "timestamp": record.event_timestamp, "metadataHash": record.metadata_hash,
                "fabricTransactionId": record.fabric_transaction_id}
