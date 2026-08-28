import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.evidence import Evidence
from app.services.evidence_ledger import EvidenceLedgerService, generate_record_hash


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()


def test_ledger_register_retrieve_verify(db_session):
    ledger = EvidenceLedgerService(db_session)

    payload = {
        "eventId": "EV-1",
        "tenantId": "tenant-a",
        "recordId": "rec-1",
        "eventType": "INVOICE_REGISTERED",
        "documentHash": "a" * 64,
        "metadataHash": "b" * 64,
        "actor": "user-1",
        "timestamp": "2026-08-28T12:00:00Z",
        "storageKey": "tenant-a/EV-1/abc.pdf"
    }

    # 1. Register
    res = ledger.register(payload)
    assert res["status"] == "REGISTERED"
    assert res["transactionId"]
    assert res["recordHash"]
    assert res["previousHash"] is None

    # 2. Get Evidence
    evidence = ledger.get_evidence("EV-1", "tenant-a")
    assert evidence["status"] == "FOUND"
    assert evidence["documentHash"] == "a" * 64
    assert evidence["recordHash"] == res["recordHash"]

    # 3. Verify Evidence
    verify_res = ledger.verify_evidence("EV-1", "a" * 64, "tenant-a")
    assert verify_res["status"] == "VERIFIED"
    assert verify_res["recordHash"] == res["recordHash"]


def test_ledger_duplicate_evidence(db_session):
    ledger = EvidenceLedgerService(db_session)
    payload = {
        "eventId": "EV-DUP",
        "tenantId": "tenant-a",
        "recordId": "rec-1",
        "eventType": "INVOICE_REGISTERED",
        "documentHash": "a" * 64,
        "metadataHash": "b" * 64,
        "actor": "user-1",
        "timestamp": "2026-08-28T12:00:00Z"
    }
    ledger.register(payload)
    with pytest.raises(ValueError, match="DUPLICATE_EVENT_ID"):
        ledger.register(payload)


def test_ledger_hash_chaining_and_tamper_detection(db_session):
    ledger = EvidenceLedgerService(db_session)

    # Record A
    payload_a = {
        "eventId": "EV-A",
        "tenantId": "tenant-a",
        "recordId": "rec-1",
        "eventType": "INVOICE_REGISTERED",
        "documentHash": "a" * 64,
        "metadataHash": "b" * 64,
        "actor": "user-1",
        "timestamp": "2026-08-28T12:00:00Z"
    }
    res_a = ledger.register(payload_a)

    # Record B (chains to A)
    payload_b = {
        "eventId": "EV-B",
        "tenantId": "tenant-a",
        "recordId": "rec-2",
        "eventType": "INVOICE_REGISTERED",
        "documentHash": "c" * 64,
        "metadataHash": "d" * 64,
        "actor": "user-1",
        "timestamp": "2026-08-28T12:01:00Z"
    }
    res_b = ledger.register(payload_b)

    assert res_b["previousHash"] == res_a["recordHash"]

    # Check chain linkage is valid
    verify_b = ledger.verify_evidence("EV-B", "c" * 64, "tenant-a")
    assert verify_b["status"] == "VERIFIED"

    # Simulate tampering: manually modify record A in database
    db_record_a = db_session.query(Evidence).filter(Evidence.fabric_event_id == "EV-A").one()
    db_record_a.document_hash = "f" * 64
    db_session.commit()

    # Verify A -> should report TAMPERED (record hash mismatch)
    verify_a_tampered = ledger.verify_evidence("EV-A", "f" * 64, "tenant-a")
    assert verify_a_tampered["status"] == "TAMPERED"

    # Verify B -> should report TAMPERED because previous hash linkage is broken
    verify_b_broken = ledger.verify_evidence("EV-B", "c" * 64, "tenant-a")
    assert verify_b_broken["status"] == "TAMPERED"


def test_ledger_tenant_isolation(db_session):
    ledger = EvidenceLedgerService(db_session)
    payload_a = {
        "eventId": "EV-A",
        "tenantId": "tenant-a",
        "recordId": "rec-1",
        "eventType": "INVOICE_REGISTERED",
        "documentHash": "a" * 64,
        "metadataHash": "b" * 64,
        "actor": "user-1",
        "timestamp": "2026-08-28T12:00:00Z"
    }
    ledger.register(payload_a)

    # Try retrieving from tenant-b -> should return NOT_REGISTERED
    res = ledger.get_evidence("EV-A", "tenant-b")
    assert res["status"] == "NOT_REGISTERED"


def test_ledger_sequence_number_ordering(db_session):
    ledger = EvidenceLedgerService(db_session)
    # Register three records with the exact same timestamp
    ts = "2026-08-28T12:00:00Z"
    
    payload1 = {
        "eventId": "EV-1", "tenantId": "tenant-a", "recordId": "r1",
        "eventType": "INVOICE_REGISTERED", "documentHash": "a"*64,
        "actor": "user-1", "timestamp": ts
    }
    payload2 = {
        "eventId": "EV-2", "tenantId": "tenant-a", "recordId": "r2",
        "eventType": "INVOICE_REGISTERED", "documentHash": "b"*64,
        "actor": "user-1", "timestamp": ts
    }
    payload3 = {
        "eventId": "EV-3", "tenantId": "tenant-a", "recordId": "r3",
        "eventType": "INVOICE_REGISTERED", "documentHash": "c"*64,
        "actor": "user-1", "timestamp": ts
    }
    
    res1 = ledger.register(payload1)
    res2 = ledger.register(payload2)
    res3 = ledger.register(payload3)
    
    assert res2["previousHash"] == res1["recordHash"]
    assert res3["previousHash"] == res2["recordHash"]
    
    # Confirm sequence numbers are sequential
    ev1 = db_session.query(Evidence).filter(Evidence.fabric_event_id == "EV-1").one()
    ev2 = db_session.query(Evidence).filter(Evidence.fabric_event_id == "EV-2").one()
    ev3 = db_session.query(Evidence).filter(Evidence.fabric_event_id == "EV-3").one()
    
    assert ev1.sequence_number < ev2.sequence_number < ev3.sequence_number


def test_ledger_full_chain_validation(db_session):
    ledger = EvidenceLedgerService(db_session)
    
    payload_a = {
        "eventId": "EV-A", "tenantId": "tenant-a", "recordId": "r1",
        "eventType": "INVOICE_REGISTERED", "documentHash": "a"*64,
        "actor": "user-1", "timestamp": "2026-08-28T12:00:00Z"
    }
    payload_b = {
        "eventId": "EV-B", "tenantId": "tenant-a", "recordId": "r2",
        "eventType": "INVOICE_REGISTERED", "documentHash": "b"*64,
        "actor": "user-1", "timestamp": "2026-08-28T12:01:00Z"
    }
    payload_c = {
        "eventId": "EV-C", "tenantId": "tenant-a", "recordId": "r3",
        "eventType": "INVOICE_REGISTERED", "documentHash": "c"*64,
        "actor": "user-1", "timestamp": "2026-08-28T12:02:00Z"
    }
    
    res_a = ledger.register(payload_a)
    res_b = ledger.register(payload_b)
    res_c = ledger.register(payload_c)
    
    # Valid complete chain checks
    verify_c = ledger.verify_evidence("EV-C", "c"*64, "tenant-a")
    assert verify_c["status"] == "VERIFIED"
    assert verify_c["depth_checked"] == 3
    
    # Corrupt a deep predecessor (EV-A)
    rec_a = db_session.query(Evidence).filter(Evidence.fabric_event_id == "EV-A").one()
    rec_a.document_hash = "f"*64
    db_session.commit()
    
    # Verifying C should now fail due to predecessor corruption!
    verify_c_corrupted = ledger.verify_evidence("EV-C", "c"*64, "tenant-a")
    assert verify_c_corrupted["status"] == "TAMPERED"


def test_ledger_cyclic_chain_detection(db_session):
    ledger = EvidenceLedgerService(db_session)
    
    payload_a = {
        "eventId": "EV-A", "tenantId": "tenant-a", "recordId": "r1",
        "eventType": "INVOICE_REGISTERED", "documentHash": "a"*64,
        "actor": "user-1", "timestamp": "2026-08-28T12:00:00Z"
    }
    payload_b = {
        "eventId": "EV-B", "tenantId": "tenant-a", "recordId": "r2",
        "eventType": "INVOICE_REGISTERED", "documentHash": "b"*64,
        "actor": "user-1", "timestamp": "2026-08-28T12:01:00Z"
    }
    
    ledger.register(payload_a)
    ledger.register(payload_b)
    
    # Force dummy cyclic hashes directly into the database
    rec_a = db_session.query(Evidence).filter(Evidence.fabric_event_id == "EV-A").one()
    rec_b = db_session.query(Evidence).filter(Evidence.fabric_event_id == "EV-B").one()
    
    rec_a.record_hash = "dummy-hash-a"
    rec_a.previous_hash = "dummy-hash-b"
    
    rec_b.record_hash = "dummy-hash-b"
    rec_b.previous_hash = "dummy-hash-a"
    
    db_session.commit()
    
    verify_cyclic = ledger.verify_evidence("EV-B", "b"*64, "tenant-a")
    assert verify_cyclic["status"] == "TAMPERED"
    assert "cyclic" in verify_cyclic["reason"]

