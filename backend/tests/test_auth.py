import pytest
from fastapi import HTTPException

from fastapi.security import HTTPAuthorizationCredentials

from app.core import auth
from app.core.auth import create_principal_token, get_current_principal
from app.core.config import Settings


def test_signed_principal_round_trip(monkeypatch):
    monkeypatch.setattr(auth, "get_settings", lambda: Settings(auth_secret="secret"))
    token = create_principal_token("tenant-a", "user-1", "secret")
    principal = get_current_principal(HTTPAuthorizationCredentials(scheme="Bearer", credentials=token))
    assert principal.tenant_id == "tenant-a"
    assert principal.actor == "user-1"


def test_invalid_signature_is_rejected(monkeypatch):
    monkeypatch.setattr(auth, "get_settings", lambda: Settings(auth_secret="secret"))
    with pytest.raises(HTTPException):
        get_current_principal(HTTPAuthorizationCredentials(scheme="Bearer", credentials="bad.token"))
