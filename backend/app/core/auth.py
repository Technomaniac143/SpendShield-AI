import base64
import hashlib
import hmac
import json
from dataclasses import dataclass

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import get_settings

bearer = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class Principal:
    tenant_id: str
    actor: str


def _encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def create_principal_token(tenant_id: str, actor: str, secret: str) -> str:
    payload = _encode(json.dumps({"tenant_id": tenant_id, "actor": actor}, separators=(",", ":")).encode())
    signature = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).digest()
    return f"{payload}.{_encode(signature)}"


def get_current_principal(credentials: HTTPAuthorizationCredentials | None = Depends(bearer)) -> Principal:
    settings = get_settings()
    if credentials is None or credentials.scheme.lower() != "bearer" or not settings.auth_secret:
        raise HTTPException(status_code=401, detail="authenticated principal required")
    try:
        payload, encoded_signature = credentials.credentials.split(".", 1)
        expected = hmac.new(settings.auth_secret.encode(), payload.encode(), hashlib.sha256).digest()
        if not hmac.compare_digest(expected, _decode(encoded_signature)):
            raise ValueError("invalid signature")
        data = json.loads(_decode(payload))
        if not data.get("tenant_id") or not data.get("actor"):
            raise ValueError("invalid principal")
        return Principal(tenant_id=data["tenant_id"], actor=data["actor"])
    except (ValueError, KeyError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise HTTPException(status_code=401, detail="invalid principal") from exc