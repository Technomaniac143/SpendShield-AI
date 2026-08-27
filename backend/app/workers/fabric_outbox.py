import json
import logging
import os
from datetime import datetime, timedelta, timezone

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, sessionmaker

from app.integrations.blockchain import FabricClient, FabricTransactionRejected, FabricUnavailable
from app.models import Evidence, FabricOutbox, OutboxStatus

logger = logging.getLogger(__name__)
MAX_ATTEMPTS = 8
LEASE_SECONDS = 300


class FabricOutboxWorker:
    def __init__(self, session_factory: sessionmaker, fabric: FabricClient):
        self.session_factory = session_factory
        self.fabric = fabric

    def process_once(self) -> bool:
        with self.session_factory() as db:
            now = datetime.now(timezone.utc)
            lease_expiry = now - timedelta(seconds=LEASE_SECONDS)
            expired = FabricOutbox.locked_at < lease_expiry
            item = db.scalar(select(FabricOutbox).where(
                or_(
                    (FabricOutbox.status == OutboxStatus.PENDING) &
                    (FabricOutbox.next_attempt_at.is_(None) | (FabricOutbox.next_attempt_at <= now)),
                    (FabricOutbox.status == OutboxStatus.PROCESSING) & expired,
                )
            ).order_by(FabricOutbox.created_at).with_for_update(skip_locked=True))
            if item is None:
                return False
            item.status = OutboxStatus.PROCESSING
            item.attempts += 1
            item.locked_at = now
            item.locked_by = f"{os.getpid()}"
            db.commit()
            try:
                result = self.fabric.register_evidence(**json.loads(item.payload))
            except FabricTransactionRejected as exc:
                try:
                    existing = self.fabric.get_evidence(item.event_id)
                    if existing.get("status") == "FOUND" and existing.get("fabricTransactionId"):
                        self._complete(db, item, existing["fabricTransactionId"])
                    else:
                        self._fail(db, item, str(exc))
                except Exception as lookup_error:
                    self._retry(db, item, lookup_error)
                return True
            except FabricUnavailable as exc:
                self._retry(db, item, exc)
                return True
            except Exception as exc:
                logger.exception("unexpected outbox processing failure", extra={"event_id": item.event_id})
                self._retry(db, item, exc)
                return True
            self._complete(db, item, result["transactionId"])
            return True

    def _retry(self, db: Session, item: FabricOutbox, error: Exception) -> None:
        item.last_error = str(error)[:4000]
        item.locked_at = None
        item.locked_by = None
        if item.attempts >= MAX_ATTEMPTS:
            item.status = OutboxStatus.FAILED
            item.processed_at = datetime.now(timezone.utc)
        else:
            item.status = OutboxStatus.PENDING
            delay = min(2 ** min(item.attempts, 8), 300)
            item.next_attempt_at = datetime.now(timezone.utc) + timedelta(seconds=delay)
        db.commit()

    @staticmethod
    def _fail(db: Session, item: FabricOutbox, error: str) -> None:
        item.status = OutboxStatus.FAILED
        item.last_error = error[:4000]
        item.locked_at = None
        item.locked_by = None
        item.processed_at = datetime.now(timezone.utc)
        db.commit()

    @staticmethod
    def _complete(db: Session, item: FabricOutbox, transaction_id: str) -> None:
        item.status = OutboxStatus.COMPLETED
        item.processed_at = datetime.now(timezone.utc)
        item.last_error = None
        item.locked_at = None
        item.locked_by = None
        item.next_attempt_at = None
        evidence = db.scalar(select(Evidence).where(Evidence.fabric_event_id == item.event_id, Evidence.tenant_id == item.tenant_id))
        if evidence:
            evidence.fabric_transaction_id = transaction_id
            evidence.verification_status = "REGISTERED"
        db.commit()