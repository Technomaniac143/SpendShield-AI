import io
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.main import app
from app.core.config import get_settings
from app.core.auth import require_permission, Principal
from app.models.evidence import Evidence
from app.core.database import SessionLocal

client = TestClient(app)


def test_database_ledger_e2e_api_flow():
    # 1. Configure backend settings
    settings = get_settings()
    original_backend = settings.evidence_ledger_backend
    settings.evidence_ledger_backend = "database"

    # 2. Inject mock principals and storage
    principal = Principal(tenant_id="tenant-a", actor="user-1", user_id="user-1")
    for route in app.routes:
        if hasattr(route, "dependant"):
            for dep in route.dependant.dependencies:
                if dep.call.__name__ == "dependency":
                    app.dependency_overrides[dep.call] = lambda: principal

    from app.api.evidence import get_storage
    from unittest.mock import Mock
    from app.integrations.storage import document_hash
    content = b"%PDF-1.4 test content"
    expected_hash = document_hash(content)

    mock_storage = Mock()
    mock_storage.hash.return_value = expected_hash
    app.dependency_overrides[get_storage] = lambda: mock_storage

    try:
        # Pre-clean database in case of leftover records from failed test runs
        db = SessionLocal()
        try:
            record = db.scalar(select(Evidence).where(Evidence.fabric_event_id == "EV-E2E-1"))
            if record:
                db.delete(record)
                db.commit()
        finally:
            db.close()

        # Create test document (valid PDF starts with %PDF-)
        pdf_file = io.BytesIO(content)

        # 3. Register Evidence
        response = client.post(
            "/api/v1/evidence/EV-E2E-1/register",
            data={
                "record_id": "rec-e2e-1",
                "event_type": "INVOICE_REGISTERED",
                "timestamp": "2026-08-28T12:00:00Z",
                "source_type": "DOCUMENT",
                "metadata_hash": "b" * 64
            },
            files={"document": ("invoice.pdf", pdf_file, "application/pdf")}
        )

        assert response.status_code == 200, response.text
        res_data = response.json()
        assert res_data["status"] == "REGISTERED"
        assert res_data["transactionId"]

        tx_id = res_data["transactionId"]

        # 4. Get Evidence
        get_res = client.get("/api/v1/evidence/EV-E2E-1")
        assert get_res.status_code == 200
        assert get_res.json()["status"] == "FOUND"

        # 5. Verify Evidence
        verify_res = client.post("/api/v1/evidence/EV-E2E-1/verify")
        assert verify_res.status_code == 200
        assert verify_res.json()["status"] == "VERIFIED"

        # 6. Retrieve History
        history_res = client.get("/api/v1/evidence/EV-E2E-1/history")
        assert history_res.status_code == 200
        assert history_res.json()["eventId"] == "EV-E2E-1"
        assert len(history_res.json()["history"]) == 1

        # 7. Retrieve Transaction Metadata
        tx_res = client.get("/api/v1/evidence/EV-E2E-1/blockchain")
        assert tx_res.status_code == 200
        tx_data = tx_res.json()
        assert tx_data["fabric"]["transaction_id"] == tx_id
        assert tx_data["fabric"]["block_number"] is None

        # Clean up database entry
        db = SessionLocal()
        try:
            record = db.scalar(select(Evidence).where(Evidence.fabric_event_id == "EV-E2E-1"))
            if record:
                db.delete(record)
                db.commit()
        finally:
            db.close()

    finally:
        # Restore settings and clear overrides
        settings.evidence_ledger_backend = original_backend
        app.dependency_overrides.clear()
