import json
import os
import subprocess
import threading
from functools import lru_cache
from pathlib import Path
from typing import Any

from app.core.config import Settings, get_settings


class FabricUnavailable(RuntimeError):
    pass


class FabricTransactionRejected(RuntimeError):
    pass


class FabricClient:
    """Thread-safe client for one long-lived JSON-lines Fabric Gateway worker."""

    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()
        self._process: subprocess.Popen[str] | None = None
        self._lock = threading.Lock()

    def _helper_path(self) -> Path:
        helper = Path(self.settings.fabric_helper_path)
        return helper if helper.is_absolute() else Path(__file__).resolve().parents[4] / helper

    def _start(self) -> subprocess.Popen[str]:
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
            return subprocess.Popen(
                ["node", str(self._helper_path())], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, text=True, bufsize=1, env={**os.environ, **environment},
            )
        except OSError as exc:
            raise FabricUnavailable("Node.js Fabric Gateway worker is unavailable") from exc

    def _call(self, operation: str, **arguments: Any) -> dict[str, Any]:
        with self._lock:
            if self._process is None or self._process.poll() is not None:
                self._process = self._start()
            assert self._process.stdin is not None and self._process.stdout is not None
            try:
                self._process.stdin.write(json.dumps({"operation": operation, "arguments": arguments}) + "\n")
                self._process.stdin.flush()
                line = self._process.stdout.readline()
            except (OSError, BrokenPipeError) as exc:
                self._discard_process()
                raise FabricUnavailable("Fabric Gateway worker connection failed") from exc
            if not line:
                error = self._process.stderr.read().strip() if self._process.stderr else ""
                self._discard_process()
                raise FabricUnavailable(error or "Fabric Gateway worker exited")
            try:
                response = json.loads(line)
            except json.JSONDecodeError as exc:
                raise FabricUnavailable("Fabric Gateway returned invalid JSON") from exc
            error = response.get("error")
            if error:
                if error.get("code") == "DUPLICATE_EVENT_ID":
                    raise FabricTransactionRejected(error.get("message", "duplicate event"))
                raise FabricUnavailable(error.get("message", "Fabric request failed"))
            return response

    def close(self) -> None:
        with self._lock:
            self._discard_process()

    def _discard_process(self) -> None:
        if self._process is not None:
            self._process.terminate()
            self._process = None

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


@lru_cache
def get_fabric_client() -> FabricClient:
    return FabricClient()
