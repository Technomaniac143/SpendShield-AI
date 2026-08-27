import json
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.integrations.blockchain import FabricClient, FabricTransactionRejected, FabricUnavailable
from app.models import Evidence, FabricOutbox, OutboxStatus


class FabricOutboxWorker:
    def __init__(self, session_factory: sessionmaker, fabric: FabricClient):
        self.session_factory = session_factory
        self.fabric = fabric

    def process_once(self) -> bool:
        with self.session_factory() as db:
            item = db.scalar(select(FabricOutbox).where(FabricOutbox.status == OutboxStatus.PENDING).order_by(FabricOutbox.created_at).with_for_update(skip_locked=True))
            if item is None:
                return False
            item.status = OutboxStatus.PROCESSING
            item.attempts += 1
            db.commit()
            try:
                result = self.fabric.register_evidence(**json.loads(item.payload))
            except FabricTransactionRejected as exc:
                existing = self.fabric.get_evidence(item.event_id)
                if existing.get("status") == "FOUND" and existing.get("fabricTransactionId"):
                    self._complete(db, item, existing["fabricTransactionId"])
                else:
                    item.status = OutboxStatus.FAILED
                    item.last_error = str(exc)
                    item.processed_at = datetime.now(timezone.utc)
                    db.commit()
                return True
            except FabricUnavailable as exc:
                item.status = OutboxStatus.PENDING
                item.last_error = str(exc)
                evidence = db.scalar(select(Evidence).where(Evidence.fabric_event_id == item.event_id, Evidence.tenant_id == item.tenant_id))
                if evidence:
                    evidence.verification_status = "PENDING_BLOCKCHAIN_VERIFICATION"
                db.commit()
                return True
            self._complete(db, item, result["transactionId"])
            return True

    @staticmethod
    def _complete(db: Session, item: FabricOutbox, transaction_id: str) -> None:
        item.status = OutboxStatus.COMPLETED
        item.processed_at = datetime.now(timezone.utc)
        item.last_error = None
        evidence = db.scalar(select(Evidence).where(Evidence.fabric_event_id == item.event_id, Evidence.tenant_id == item.tenant_id))
        if evidence:
            evidence.fabric_transaction_id = transaction_id
            evidence.verification_status = "REGISTERED"
        db.commit()