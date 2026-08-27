import os

import pytest

from app.integrations.blockchain import FabricClient


pytestmark = pytest.mark.integration


@pytest.mark.skipif(os.getenv("RUN_FABRIC_INTEGRATION") != "1", reason="set RUN_FABRIC_INTEGRATION=1 with a running Fabric test network")
def test_real_fabric_registration_query_and_history():
    client = FabricClient()
    result = client.register_evidence(
        eventId="INTEGRATION-EV-001", tenantId="integration-tenant", recordId="INV-1001",
        eventType="INVOICE_REGISTERED", documentHash="a" * 64, actor="integration-user",
        timestamp="2026-08-27T17:00:00Z", metadataHash="b" * 64,
    )
    assert result["transactionId"]
    assert client.get_evidence("INTEGRATION-EV-001")["status"] == "FOUND"
    assert client.verify_evidence("INTEGRATION-EV-001", "a" * 64)["status"] == "VERIFIED"
    history = client.get_history("INTEGRATION-EV-001")
    assert history["history"]
    metadata = client.get_transaction(result["transactionId"])
    assert metadata["blockNumber"] >= 0
    assert len(metadata["blockHash"]) == 64
