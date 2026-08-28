import hashlib
import json
import logging
from typing import Any, Optional
from uuid import uuid4

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.evidence import Evidence

logger = logging.getLogger(__name__)


def generate_record_hash(payload: dict) -> str:
    canonical_json = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()


class EvidenceLedgerService:
    def __init__(self, db: Session):
        self.db = db

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_record_by_hash(self, record_hash: str) -> Optional[Evidence]:
        return self.db.scalar(select(Evidence).where(Evidence.record_hash == record_hash))

    def _compute_canonical(self, record: Evidence) -> dict:
        """Reproduce the canonical dict that was hashed at registration time."""
        return {
            "actor": record.created_by,
            "documentHash": record.document_hash,
            "eventId": record.fabric_event_id,
            "eventType": record.event_type,
            "metadataHash": record.metadata_hash or "",
            "previousHash": record.previous_hash or "",
            "recordId": record.record_id,
            "tenantId": record.tenant_id,
            "timestamp": record.event_timestamp,
        }

    def get_latest_hash(self, tenant_id: str) -> Optional[str]:
        """Return the record_hash of the highest-sequence record for this tenant."""
        stmt = (
            select(Evidence.record_hash)
            .where(Evidence.tenant_id == tenant_id)
            .order_by(Evidence.sequence_number.desc())
            .limit(1)
        )
        return self.db.scalar(stmt)

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(self, payload: dict) -> dict:
        event_id = payload["eventId"]
        tenant_id = payload["tenantId"]

        # Duplicate check
        existing = self.db.scalar(
            select(Evidence).where(Evidence.fabric_event_id == event_id)
        )
        if existing:
            raise ValueError(f"DUPLICATE_EVENT_ID: {event_id}")

        # Previous hash — must be read inside the same write transaction to
        # prevent interleaving.  SQLite serialises writes; PostgreSQL uses
        # SERIALIZABLE transaction isolation for the worker process.
        prev_hash = self.get_latest_hash(tenant_id)

        # Next sequence number (global, not per-tenant, so the column UNIQUE
        # constraint protects against duplicates on concurrent writes).
        max_seq = self.db.scalar(select(func.max(Evidence.sequence_number))) or 0
        next_seq = max_seq + 1

        canonical_payload = {
            "actor": payload["actor"],
            "documentHash": payload["documentHash"].lower(),
            "eventId": event_id,
            "eventType": payload["eventType"],
            "metadataHash": payload["metadataHash"].lower() if payload.get("metadataHash") else "",
            "previousHash": prev_hash or "",
            "recordId": payload["recordId"],
            "tenantId": tenant_id,
            "timestamp": payload["timestamp"],
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
            sequence_number=next_seq,
            verification_status="REGISTERED",
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
            "previousHash": prev_hash,
        }

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

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
            "recordHash": record.record_hash,
            "sequenceNumber": record.sequence_number,
        }

    # ------------------------------------------------------------------
    # Verification — full chain walk
    # ------------------------------------------------------------------

    def verify_evidence(
        self,
        event_id: str,
        current_document_hash: str,
        tenant_id: Optional[str] = None,
    ) -> dict:
        """
        Walk the entire hash chain from `event_id` back to the genesis record.

        Checks at every node:
        1. Record exists (broken-link detection).
        2. Tenant isolation — no cross-tenant pointer.
        3. Recomputed record_hash matches stored value (tamper detection).

        Tail-node only:
        4. Live document hash matches stored document hash.

        Returns:
            {"status": "VERIFIED", "depth_checked": N, ...}
            {"status": "TAMPERED", "reason": "...", ...}
            {"status": "INTEGRITY_FAILURE", ...}  (file tampered)
            {"status": "NOT_REGISTERED", ...}
        """
        evidence_resp = self.get_evidence(event_id, tenant_id)
        if evidence_resp["status"] != "FOUND":
            return {"status": "NOT_REGISTERED", "eventId": event_id}

        # --- Tail-node live document hash check ---
        if evidence_resp["documentHash"] != current_document_hash.lower():
            return {
                "status": "INTEGRITY_FAILURE",
                "eventId": event_id,
                "reason": "document hash mismatch — file may have been tampered",
            }

        # --- Build chain from tail → genesis, detecting cycles / broken links ---
        chain: list[Evidence] = []
        visited_hashes: set[str] = set()
        max_depth = 10_000

        tail_record = self.db.scalar(
            select(Evidence).where(Evidence.fabric_event_id == event_id)
        )
        chain.append(tail_record)
        visited_hashes.add(tail_record.record_hash)
        current_ptr = tail_record.previous_hash

        while current_ptr is not None:
            if len(chain) >= max_depth:
                return {
                    "status": "TAMPERED",
                    "eventId": event_id,
                    "reason": "maximum chain traversal depth exceeded",
                }
            if current_ptr in visited_hashes:
                return {
                    "status": "TAMPERED",
                    "eventId": event_id,
                    "reason": "cyclic reference detected in ledger chain",
                }
            prev_rec = self._get_record_by_hash(current_ptr)
            if prev_rec is None:
                return {
                    "status": "TAMPERED",
                    "eventId": event_id,
                    "reason": "predecessor record not found — chain link broken",
                }
            if tenant_id and prev_rec.tenant_id != tenant_id:
                return {
                    "status": "TAMPERED",
                    "eventId": event_id,
                    "reason": "cross-tenant reference detected in chain",
                }
            visited_hashes.add(current_ptr)
            chain.append(prev_rec)
            current_ptr = prev_rec.previous_hash

        # --- Cryptographic integrity of EVERY node ---
        for rec in chain:
            canonical = self._compute_canonical(rec)
            recomputed = generate_record_hash(canonical)
            if recomputed != rec.record_hash:
                return {
                    "status": "TAMPERED",
                    "eventId": rec.fabric_event_id,
                    "reason": (
                        f"record hash mismatch for event '{rec.fabric_event_id}' "
                        f"(sequence {rec.sequence_number}) — data has been tampered"
                    ),
                }

        return {
            "status": "VERIFIED",
            "eventId": event_id,
            "registeredHash": evidence_resp["documentHash"],
            "currentHash": current_document_hash.lower(),
            "recordHash": evidence_resp["recordHash"],
            "depth_checked": len(chain),
        }

    # ------------------------------------------------------------------
    # History / Transaction
    # ------------------------------------------------------------------

    def get_history(self, event_id: str, tenant_id: Optional[str] = None) -> dict:
        evidence_resp = self.get_evidence(event_id, tenant_id)
        if evidence_resp["status"] != "FOUND":
            return {"eventId": event_id, "history": []}

        history_item = {
            "txId": evidence_resp["fabricTransactionId"],
            "timestamp": evidence_resp["timestamp"],
            "isDelete": False,
            "eventType": evidence_resp["eventType"],
            "actor": evidence_resp["actor"],
            "recordHash": evidence_resp["recordHash"],
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
                "recordHash": evidence_resp["recordHash"],
            },
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
            "chaincode": record.fabric_chaincode,
        }
