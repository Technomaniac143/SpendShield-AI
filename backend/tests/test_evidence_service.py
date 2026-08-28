from unittest.mock import Mock

from app.core.auth import Principal
from app.schemas import RegisterEvidenceRequest
from app.services.evidence import EvidenceService


def request():
    return RegisterEvidenceRequest(record_id="INV-1001", event_type="INVOICE_REGISTERED",
                                   timestamp="2026-08-27T17:00:00Z")


def test_service_passes_hashes_only_and_returns_real_transaction_id():
    db = Mock()
    db.scalar.return_value = None
    fabric = Mock()
    storage = Mock()
    service = EvidenceService(db, fabric, storage)
    service.settings.evidence_ledger_backend = "fabric"
    response = service.register("EV-001", request(), Principal("tenant-a", "user-1"), b"pdf")
    assert response == {"status": "PENDING_BLOCKCHAIN_VERIFICATION", "eventId": "EV-001"}
    storage.put.assert_called_once()
    payload = db.add_all.call_args.args[0][1].payload
    assert "pdf" not in payload
    assert len(__import__("json").loads(payload)["documentHash"]) == 64
    fabric.register_evidence.assert_not_called()
