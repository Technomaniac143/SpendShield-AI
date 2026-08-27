import json
import subprocess
from pathlib import Path
from typing import Any

from app.core.config import Settings, get_settings


class FabricUnavailable(RuntimeError):
    pass


class FabricTransactionRejected(RuntimeError):
    pass


class FabricClient:
    """Thin transport adapter; validation and procurement policy stay in the service."""

    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()

    def _call(self, operation: str, **arguments: Any) -> dict[str, Any]:
        helper = Path(self.settings.fabric_helper_path)
        if not helper.is_absolute():
            helper = Path(__file__).resolve().parents[4] / helper
        request = {"operation": operation, "arguments": arguments}
        environment = {
            "FABRIC_GATEWAY_URL": self.settings.fabric_gateway_url,
            "FABRIC_CHANNEL": self.settings.fabric_channel,
            "FABRIC_CHAINCODE": self.settings.fabric_chaincode,
            "FABRIC_CERT_PATH": self.settings.fabric_cert_path,
            "FABRIC_KEY_PATH": self.settings.fabric_key_path,
            "FABRIC_TLS_CERT_PATH": self.settings.fabric_tls_cert_path,
            "FABRIC_MSP_ID": self.settings.fabric_msp_id,
            "FABRIC_PEER_ENDPOINT": self.settings.fabric_peer_endpoint,
            "FABRIC_PEER_HOST_ALIAS": self.settings.fabric_peer_host_alias,
        }
        try:
            result = subprocess.run(
                ["node", str(helper)], input=json.dumps(request), text=True,
                capture_output=True, check=False, env={**__import__("os").environ, **environment},
            )
        except OSError as exc:
            raise FabricUnavailable("Node.js Fabric Gateway helper is unavailable") from exc
        if result.returncode != 0:
            if "evidence already exists" in result.stderr:
                raise FabricTransactionRejected(result.stderr.strip())
            raise FabricUnavailable(result.stderr.strip() or "Fabric Gateway request failed")
        try:
            response = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise FabricUnavailable("Fabric Gateway returned invalid JSON") from exc
        if response.get("error"):
            raise FabricUnavailable(response["error"])
        return response

    def register_evidence(self, **fields: str) -> dict[str, Any]:
        return self._call("registerEvidence", **fields)

    def get_evidence(self, event_id: str) -> dict[str, Any]:
        return self._call("getEvidence", eventId=event_id)

    def verify_evidence(self, event_id: str, current_document_hash: str) -> dict[str, Any]:
        return self._call("verifyEvidence", eventId=event_id, currentDocumentHash=current_document_hash)

    def get_history(self, event_id: str) -> dict[str, Any]:
        return self._call("getEvidenceHistory", eventId=event_id)

    def get_transaction(self, transaction_id: str) -> dict[str, Any]:
        return self._call("getTransaction", transactionId=transaction_id)
