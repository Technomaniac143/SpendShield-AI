from unittest.mock import Mock

from app.schemas import RegisterEvidenceRequest
from app.services.evidence import EvidenceService
from app.utils import sha256_bytes


def request(tenant="tenant-a"):
    return RegisterEvidenceRequest(tenant_id=tenant, record_id="INV-1001", event_type="INVOICE_REGISTERED",
                                   document_hash=sha256_bytes(b"pdf"), actor="user-1", timestamp="2026-08-27T17:00:00Z",
                                   metadata_hash=sha256_bytes(b"metadata"))


def test_service_passes_hashes_only_and_returns_real_transaction_id():
    db = Mock()
    fabric = Mock()
    fabric.register_evidence.return_value = {"transactionId": "real-fabric-tx"}
    service = EvidenceService(db, fabric)
    response = service.register("EV-001", request())
    assert response["fabricTransactionId"] == "real-fabric-tx"
    call = fabric.register_evidence.call_args.kwargs
    assert "pdf" not in str(call)
    assert call["documentHash"] == sha256_bytes(b"pdf")
