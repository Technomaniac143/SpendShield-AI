import pytest
import time
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


def test_malformed_encoding_is_rejected_with_401(monkeypatch):
    monkeypatch.setattr(auth, "get_settings", lambda: Settings(auth_secret="secret"))
    with pytest.raises(HTTPException) as error:
        get_current_principal(HTTPAuthorizationCredentials(scheme="Bearer", credentials="!!!!.!!!!"))
    assert error.value.status_code == 401


def test_expired_token_is_rejected(monkeypatch):
    token = create_principal_token("tenant-a", "user-1", "secret")
    monkeypatch.setattr(auth, "time", type("Clock", (), {"time": staticmethod(lambda: time.time() + 901)}))
    with pytest.raises(HTTPException):
        get_current_principal(HTTPAuthorizationCredentials(scheme="Bearer", credentials=token))
