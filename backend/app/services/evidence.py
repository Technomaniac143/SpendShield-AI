from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.integrations.blockchain import FabricClient, FabricTransactionRejected, FabricUnavailable
from app.models import Evidence
from app.schemas import RegisterEvidenceRequest
from app.utils import is_sha256

SUPPORTED_EVENT_TYPES = {
    "INVOICE_REGISTERED", "GRN_REGISTERED", "PAYMENT_APPROVED", "PAYMENT_BLOCKED",
    "DISPUTE_CREATED", "DOCUMENT_VERIFIED", "DOCUMENT_INTEGRITY_FAILED",
    "RECOMMENDATION_ACCEPTED", "RECOMMENDATION_REJECTED", "OUTCOME_RECORDED",
}


class EvidenceService:
    def __init__(self, db: Session, fabric: FabricClient):
        self.db = db
        self.fabric = fabric
        self.settings = get_settings()

    def register(self, event_id: str, request: RegisterEvidenceRequest) -> dict[str, Any]:
        if not is_sha256(request.document_hash) or not is_sha256(request.metadata_hash):
            raise ValueError("document_hash and metadata_hash must be SHA-256 hexadecimal values")
        if request.event_type not in SUPPORTED_EVENT_TYPES:
            raise ValueError("unsupported event_type")
        existing = self.db.scalar(select(Evidence).where(Evidence.tenant_id == request.tenant_id,
                                                        Evidence.fabric_event_id == event_id))
        if existing and existing.verification_status == "REGISTERED":
            return self.to_response(existing, "ALREADY_REGISTERED")
        record = existing or Evidence(tenant_id=request.tenant_id, source_type=request.source_type, source_id=request.source_id,
                                      record_id=request.record_id, event_type=request.event_type,
                                      document_hash=request.document_hash.lower(), metadata_hash=request.metadata_hash.lower(),
                                      created_by=request.actor, event_timestamp=request.timestamp,
                                      fabric_event_id=event_id, fabric_channel=self.settings.fabric_channel,
                                      fabric_chaincode=self.settings.fabric_chaincode)
        try:
            if existing is None:
                self.db.add(record)
                self.db.flush()
            result = self.fabric.register_evidence(eventId=event_id, tenantId=request.tenant_id, recordId=request.record_id,
                                                   eventType=request.event_type, documentHash=request.document_hash.lower(),
                                                   actor=request.actor, timestamp=request.timestamp,
                                                   metadataHash=request.metadata_hash.lower())
            record.fabric_transaction_id = result.get("transactionId")
            record.verification_status = "REGISTERED"
            self.db.commit()
            return {"status": "REGISTERED", "eventId": event_id, "fabricTransactionId": record.fabric_transaction_id,
                    "channel": self.settings.fabric_channel, "chaincode": self.settings.fabric_chaincode}
        except FabricTransactionRejected as exc:
            self.db.rollback()
            raise ValueError("event_id is already registered on Fabric") from exc
        except FabricUnavailable:
            self.db.rollback()
            record.verification_status = "PENDING_BLOCKCHAIN_VERIFICATION"
            self.db.add(record)
            self.db.commit()
            return {"status": "PENDING_BLOCKCHAIN_VERIFICATION", "eventId": event_id}
        except IntegrityError:
            self.db.rollback()
            raise ValueError("event_id is already registered for this tenant")

    def verify(self, event_id: str, tenant_id: str, current_document_hash: str) -> dict[str, str]:
        if not is_sha256(current_document_hash):
            raise ValueError("current_document_hash must be a SHA-256 hexadecimal value")
        record = self.db.scalar(select(Evidence).where(Evidence.tenant_id == tenant_id,
                                                        Evidence.fabric_event_id == event_id))
        if record is None:
            return {"status": "NOT_REGISTERED", "eventId": event_id}
        status = "VERIFIED" if record.document_hash == current_document_hash.lower() else "INTEGRITY_FAILURE"
        return {"status": status, "eventId": event_id, "registeredHash": record.document_hash,
                "currentHash": current_document_hash.lower()}

    @staticmethod
    def to_response(record: Evidence, status: str) -> dict[str, Any]:
        return {"status": status, "eventId": record.fabric_event_id, "tenantId": record.tenant_id,
                "recordId": record.record_id, "eventType": record.event_type, "documentHash": record.document_hash,
                "actor": record.created_by, "timestamp": record.event_timestamp, "metadataHash": record.metadata_hash,
                "fabricTransactionId": record.fabric_transaction_id}
