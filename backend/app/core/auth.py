import base64
import binascii
import hashlib
import hmac
import json
import os
import secrets
import time
from dataclasses import dataclass
from uuid import uuid4

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db

bearer = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class Principal:
    tenant_id: str
    actor: str
    user_id: str | None = None


def _encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


TOKEN_TTL_SECONDS = 900


def create_principal_token(
    tenant_id: str,
    actor: str,
    secret: str,
    user_id: str | None = None,
    ttl_seconds: int = TOKEN_TTL_SECONDS,
) -> str:
    now = int(time.time())
    payload = _encode(json.dumps({
        "tenant_id": tenant_id,
        "actor": actor,
        "iat": now,
        "exp": now + ttl_seconds,
        "jti": str(uuid4()),
    }, separators=(",", ":")).encode())
    if user_id:
        payload = _encode(json.dumps({
            "tenant_id": tenant_id,
            "actor": actor,
            "user_id": user_id,
            "iat": now,
            "exp": now + ttl_seconds,
            "jti": str(uuid4()),
        }, separators=(",", ":")).encode())
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
        now = int(time.time())
        if (
            not isinstance(data.get("tenant_id"), str)
            or not data["tenant_id"]
            or not isinstance(data.get("actor"), str)
            or not data["actor"]
            or not isinstance(data.get("exp"), int)
            or data["exp"] <= now
            or not isinstance(data.get("iat"), int)
            or data["iat"] > now + 30
            or not isinstance(data.get("jti"), str)
        ):
            raise ValueError("invalid principal")
        user_id = data.get("user_id")
        if user_id is not None and (not isinstance(user_id, str) or not user_id):
            raise ValueError("invalid user")
        return Principal(tenant_id=data["tenant_id"], actor=data["actor"], user_id=user_id)
    except (ValueError, KeyError, json.JSONDecodeError, UnicodeDecodeError, binascii.Error) as exc:
        raise HTTPException(status_code=401, detail="invalid principal") from exc


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1, dklen=32)
    return f"scrypt$16384$8$1${_encode(salt)}${_encode(digest)}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, n, r, p, encoded_salt, encoded_digest = encoded.split("$", 5)
        if algorithm != "scrypt":
            return False
        digest = hashlib.scrypt(
            password.encode(), salt=_decode(encoded_salt), n=int(n), r=int(r), p=int(p), dklen=32,
        )
        return hmac.compare_digest(digest, _decode(encoded_digest))
    except (ValueError, TypeError, UnicodeError, binascii.Error):
        return False


def new_refresh_token() -> str:
    return secrets.token_urlsafe(48)


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def require_permission(permission: str):
    def dependency(principal: Principal = Depends(get_current_principal), db: Session = Depends(get_db)) -> Principal:
        if principal.user_id is None:
            raise HTTPException(status_code=403, detail="permission denied")
        from app.models import Tenant, User

        user = db.scalar(select(User).where(
            User.id == principal.user_id,
            User.tenant_id == principal.tenant_id,
            User.active.is_(True),
        ))
        tenant = db.get(Tenant, principal.tenant_id)
        if user is None or tenant is None or not tenant.active:
            raise HTTPException(status_code=401, detail="user session required")
        from app.services.auth import permissions_for

        user_permissions = permissions_for(db, principal.user_id)
        if permission not in user_permissions:
            raise HTTPException(status_code=403, detail="permission denied")
        return principal

    return dependency
