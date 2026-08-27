import hashlib
import json
import logging
from typing import Any, Optional
from uuid import uuid4
from sqlalchemy import select, desc
from sqlalchemy.orm import Session

from app.models.evidence import Evidence

logger = logging.getLogger(__name__)


def generate_record_hash(payload: dict) -> str:
    canonical_json = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()


class EvidenceLedgerService:
    def __init__(self, db: Session):
        self.db = db

    def get_latest_hash(self, tenant_id: str) -> Optional[str]:
        stmt = (
            select(Evidence.record_hash)
            .where(Evidence.tenant_id == tenant_id)
            .order_by(desc(Evidence.created_at), desc(Evidence.evidence_id))
            .limit(1)
        )
        return self.db.scalar(stmt)

    def register(self, payload: dict) -> dict:
        event_id = payload["eventId"]
        tenant_id = payload["tenantId"]

        # Check duplicate Event ID
        existing = self.db.scalar(select(Evidence).where(Evidence.fabric_event_id == event_id))
        if existing:
            raise ValueError(f"DUPLICATE_EVENT_ID: {event_id}")

        # Hash Chaining
        prev_hash = self.get_latest_hash(tenant_id)

        canonical_payload = {
            "actor": payload["actor"],
            "documentHash": payload["documentHash"].lower(),
            "eventId": event_id,
            "eventType": payload["eventType"],
            "metadataHash": payload["metadataHash"].lower() if payload.get("metadataHash") else "",
            "previousHash": prev_hash or "",
            "recordId": payload["recordId"],
            "tenantId": tenant_id,
            "timestamp": payload["timestamp"]
        }

        rec_hash = generate_record_hash(canonical_payload)
        tx_id = str(uuid4())

        record = Evidence(
            tenant_id=tenant_id,
            source_type="DOCUMENT",
            storage_key=payload.get("storageKey", ""),
            record_id=payload["recordId"],
            event_type=payload["eventType"],
            document_hash=payload["documentHash"].lower(),
            metadata_hash=payload["metadataHash"].lower() if payload.get("metadataHash") else "",
            created_by=payload["actor"],
            event_timestamp=payload["timestamp"],
            fabric_event_id=event_id,
            fabric_transaction_id=tx_id,
            fabric_channel="local",
            fabric_chaincode="spendshield",
            previous_hash=prev_hash,
            record_hash=rec_hash,
            verification_status="REGISTERED"
        )

        self.db.add(record)
        self.db.commit()

        return {
            "status": "REGISTERED",
            "eventId": event_id,
            "tenantId": tenant_id,
            "recordId": payload["recordId"],
            "eventType": payload["eventType"],
            "documentHash": payload["documentHash"].lower(),
            "actor": payload["actor"],
            "timestamp": payload["timestamp"],
            "metadataHash": payload["metadataHash"].lower() if payload.get("metadataHash") else "",
            "transactionId": tx_id,
            "recordHash": rec_hash,
            "previousHash": prev_hash
        }

    def get_evidence(self, event_id: str, tenant_id: Optional[str] = None) -> dict:
        stmt = select(Evidence).where(Evidence.fabric_event_id == event_id)
        if tenant_id:
            stmt = stmt.where(Evidence.tenant_id == tenant_id)
        record = self.db.scalar(stmt)
        if not record:
            return {"status": "NOT_REGISTERED", "eventId": event_id}

        return {
            "status": "FOUND",
            "eventId": record.fabric_event_id,
            "tenantId": record.tenant_id,
            "recordId": record.record_id,
            "eventType": record.event_type,
            "documentHash": record.document_hash,
            "actor": record.created_by,
            "timestamp": record.event_timestamp,
            "metadataHash": record.metadata_hash,
            "fabricTransactionId": record.fabric_transaction_id,
            "previousHash": record.previous_hash,
            "recordHash": record.record_hash
        }

    def verify_evidence(self, event_id: str, current_document_hash: str, tenant_id: Optional[str] = None) -> dict:
        evidence_resp = self.get_evidence(event_id, tenant_id)
        if evidence_resp["status"] != "FOUND":
            return {"status": "NOT_REGISTERED", "eventId": event_id}

        if evidence_resp["documentHash"] != current_document_hash.lower():
            return {
                "status": "INTEGRITY_FAILURE",
                "eventId": event_id,
                "reason": "document hash mismatch"
            }

        # Verify cryptographic integrity of record hash
        canonical = {
            "actor": evidence_resp["actor"],
            "documentHash": evidence_resp["documentHash"],
            "eventId": event_id,
            "eventType": evidence_resp["eventType"],
            "metadataHash": evidence_resp["metadataHash"],
            "previousHash": evidence_resp["previousHash"] or "",
            "recordId": evidence_resp["recordId"],
            "tenantId": evidence_resp["tenantId"],
            "timestamp": evidence_resp["timestamp"]
        }
        recomputed = generate_record_hash(canonical)
        if recomputed != evidence_resp["recordHash"]:
            return {
                "status": "TAMPERED",
                "eventId": event_id,
                "reason": "record hash mismatch"
            }

        # Verify hash linkage to previous record
        if evidence_resp["previousHash"]:
            stmt_prev = select(Evidence).where(Evidence.record_hash == evidence_resp["previousHash"])
            prev_rec = self.db.scalar(stmt_prev)
            if not prev_rec:
                return {
                    "status": "TAMPERED",
                    "eventId": event_id,
                    "reason": "predecessor record not found or link broken"
                }
            canonical_prev = {
                "actor": prev_rec.created_by,
                "documentHash": prev_rec.document_hash,
                "eventId": prev_rec.fabric_event_id,
                "eventType": prev_rec.event_type,
                "metadataHash": prev_rec.metadata_hash,
                "previousHash": prev_rec.previous_hash or "",
                "recordId": prev_rec.record_id,
                "tenantId": prev_rec.tenant_id,
                "timestamp": prev_rec.event_timestamp
            }
            if generate_record_hash(canonical_prev) != evidence_resp["previousHash"]:
                return {
                    "status": "TAMPERED",
                    "eventId": event_id,
                    "reason": "predecessor record has been tampered"
                }

        return {
            "status": "VERIFIED",
            "eventId": event_id,
            "registeredHash": evidence_resp["documentHash"],
            "currentHash": current_document_hash.lower(),
            "recordHash": evidence_resp["recordHash"]
        }

    def get_history(self, event_id: str, tenant_id: Optional[str] = None) -> dict:
        evidence_resp = self.get_evidence(event_id, tenant_id)
        if evidence_resp["status"] != "FOUND":
            return {"eventId": event_id, "history": []}

        # History in SQLite database ledger: returns the single immutable record of this event
        history_item = {
            "txId": evidence_resp["fabricTransactionId"],
            "timestamp": evidence_resp["timestamp"],
            "isDelete": False,
            "value": {
                "eventId": event_id,
                "tenantId": evidence_resp["tenantId"],
                "recordId": evidence_resp["recordId"],
                "eventType": evidence_resp["eventType"],
                "documentHash": evidence_resp["documentHash"],
                "actor": evidence_resp["actor"],
                "timestamp": evidence_resp["timestamp"],
                "metadataHash": evidence_resp["metadataHash"],
                "previousHash": evidence_resp["previousHash"],
                "recordHash": evidence_resp["recordHash"]
            }
        }
        return {"eventId": event_id, "history": [history_item]}

    def get_transaction(self, tx_id: str) -> dict:
        stmt = select(Evidence).where(Evidence.fabric_transaction_id == tx_id)
        record = self.db.scalar(stmt)
        if not record:
            return {"status": "NOT_FOUND", "transactionId": tx_id}
        return {
            "transactionId": tx_id,
            "eventId": record.fabric_event_id,
            "timestamp": record.event_timestamp,
            "recordHash": record.record_hash,
            "status": "COMMITTED",
            "channel": record.fabric_channel,
            "chaincode": record.fabric_chaincode
        }
