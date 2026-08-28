import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.core.auth import Principal, hash_password, require_permission
from app.core.database import Base
from app.core.config import Settings
from app.models import Permission, RefreshSession, Role, Tenant, User, role_permissions, user_roles
from app.schemas import LoginRequest, RefreshRequest, UserUpdateRequest
from app.services import auth as auth_service


@pytest.fixture
def db():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    engine.dispose()


def seed_user(db: Session, role_name: str = "ADMIN") -> User:
    tenant = Tenant(name="Tenant A")
    role = Role(name=role_name)
    permission = Permission(name="admin:users")
    db.add_all([tenant, role, permission])
    db.flush()
    db.execute(role_permissions.insert().values(role_id=role.id, permission_id=permission.id))
    user = User(tenant_id=tenant.id, email="admin@example.com", display_name="Admin", password_hash=hash_password("password123"))
    db.add(user)
    db.flush()
    db.execute(user_roles.insert().values(user_id=user.id, role_id=role.id))
    db.commit()
    return user


def test_refresh_rotation_revokes_session_family_on_reuse(db, monkeypatch):
    user = seed_user(db)
    monkeypatch.setattr(auth_service, "get_settings", lambda: Settings(auth_secret="test-secret"))

    issued = auth_service.login(db, LoginRequest(tenant_id=user.tenant_id, email=user.email, password="password123"))
    family_id = db.scalar(select(RefreshSession.family_id))
    rotated = auth_service.refresh(db, RefreshRequest(refresh_token=issued["refresh_token"]))
    assert rotated["refresh_token"] != issued["refresh_token"]

    with pytest.raises(auth_service.AuthenticationError):
        auth_service.refresh(db, RefreshRequest(refresh_token=issued["refresh_token"]))
    with pytest.raises(auth_service.AuthenticationError):
        auth_service.refresh(db, RefreshRequest(refresh_token=rotated["refresh_token"]))

    sessions = list(db.scalars(select(RefreshSession).where(RefreshSession.family_id == family_id)))
    assert sessions and all(session.revoked_at is not None for session in sessions)


def test_permissions_are_resolved_from_role_assignments(db):
    user = seed_user(db)
    assert auth_service.permissions_for(db, user.id) == {"admin:users"}

    user.active = False
    db.commit()
    with pytest.raises(HTTPException) as error:
        require_permission("admin:users")(Principal(user.tenant_id, user.email, user.id), db)
    assert error.value.status_code == 401

    other = Tenant(name="Tenant B")
    db.add(other)
    db.commit()
    with pytest.raises(auth_service.AuthenticationError):
        auth_service.update_user(db, other.id, user, UserUpdateRequest(display_name="Hijack"))