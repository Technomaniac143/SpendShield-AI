from typing import Dict, Any
import datetime
import uuid

class FabricClientMock:
    """
    Mocks Hyperledger Fabric integration for the MVP.
    In production, this uses the fabric-gateway SDK.
    """
    def __init__(self):
        self.channel = "spendshield-channel"
        
    async def register_event(self, tenant_id: str, record_id: str, event_type: str, document_hash: str, actor: str) -> Dict[str, Any]:
        """
        Registers an event on the blockchain.
        """
        # Mocking blockchain transaction
        tx_id = f"tx_{uuid.uuid4().hex}"
        timestamp = datetime.datetime.utcnow().isoformat()
        
        return {
            "status": "SUCCESS",
            "transaction_id": tx_id,
            "timestamp": timestamp,
            "event": {
                "tenant_id": tenant_id,
                "record_id": record_id,
                "event_type": event_type,
                "document_hash": document_hash,
                "actor": actor
            }
        }

fabric_client = FabricClientMock()
