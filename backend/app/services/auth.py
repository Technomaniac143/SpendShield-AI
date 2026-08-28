from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from app.core.auth import (
    TOKEN_TTL_SECONDS,
    Principal,
    create_principal_token,
    hash_password,
    hash_refresh_token,
    new_refresh_token,
    verify_password,
)
from app.core.config import get_settings
from app.models import Permission, RefreshSession, Role, Tenant, User, role_permissions, user_roles
from app.schemas import LoginRequest, RefreshRequest, UserCreateRequest, UserUpdateRequest

DEFAULT_ROLE = "VIEWER"


class AuthenticationError(ValueError):
    pass


def _roles(db: Session, user_id: str) -> list[str]:
    return list(db.scalars(
        select(Role.name).join(user_roles, user_roles.c.role_id == Role.id).where(user_roles.c.user_id == user_id)
    ))


def _token_response(db: Session, user: User, refresh: str) -> dict:
    settings = get_settings()
    return {
        "access_token": create_principal_token(
            user.tenant_id, user.email, settings.auth_secret, user.id, settings.access_token_ttl_seconds,
        ),
        "refresh_token": refresh,
        "token_type": "bearer",
        "expires_in": settings.access_token_ttl_seconds,
    }


def login(db: Session, request: LoginRequest) -> dict:
    tenant_id = request.tenant_id
    if not tenant_id:
        user = db.scalar(select(User).where(User.email == request.email.lower()))
        if user:
            tenant_id = user.tenant_id
    else:
        user = db.scalar(select(User).where(User.tenant_id == tenant_id, User.email == request.email.lower()))

    tenant = db.get(Tenant, tenant_id) if tenant_id else None
    if tenant is None or not tenant.active or user is None or not user.active or not verify_password(request.password, user.password_hash):
        raise AuthenticationError("invalid credentials")

    refresh = new_refresh_token()
    db.add(RefreshSession(
        user_id=user.id, tenant_id=user.tenant_id, family_id=str(uuid4()),
        token_hash=hash_refresh_token(refresh),
        expires_at=datetime.now(timezone.utc) + timedelta(days=get_settings().refresh_token_ttl_days),
    ))
    db.commit()
    return _token_response(db, user, refresh)


def refresh(db: Session, request: RefreshRequest) -> dict:
    token_hash = hash_refresh_token(request.refresh_token)
    session = db.scalar(select(RefreshSession).where(RefreshSession.token_hash == token_hash).with_for_update())
    if session is None:
        raise AuthenticationError("invalid refresh token")
    if session.revoked_at is not None:
        db.execute(update(RefreshSession).where(RefreshSession.family_id == session.family_id).values(revoked_at=datetime.now(timezone.utc)))
        db.commit()
        raise AuthenticationError("refresh token reuse detected")
    expires_at = session.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at <= datetime.now(timezone.utc):
        session.revoked_at = datetime.now(timezone.utc)
        db.commit()
        raise AuthenticationError("refresh token expired")

    user = db.scalar(select(User).where(User.id == session.user_id, User.tenant_id == session.tenant_id))
    if user is None or not user.active:
        raise AuthenticationError("user is inactive")
    replacement = new_refresh_token()
    replacement_hash = hash_refresh_token(replacement)
    session.revoked_at = datetime.now(timezone.utc)
    session.replaced_by_hash = replacement_hash
    db.add(RefreshSession(
        user_id=session.user_id, tenant_id=session.tenant_id, family_id=session.family_id,
        token_hash=replacement_hash,
        expires_at=datetime.now(timezone.utc) + timedelta(days=get_settings().refresh_token_ttl_days),
    ))
    db.commit()
    return _token_response(db, user, replacement)


def logout(db: Session, request: RefreshRequest) -> None:
    session = db.scalar(select(RefreshSession).where(RefreshSession.token_hash == hash_refresh_token(request.refresh_token)))
    if session is not None:
        db.execute(update(RefreshSession).where(RefreshSession.family_id == session.family_id).values(revoked_at=datetime.now(timezone.utc)))
        db.commit()


def create_user(db: Session, tenant_id: str, request: UserCreateRequest) -> User:
    user = User(
        tenant_id=tenant_id, email=request.email.lower(), display_name=request.display_name,
        password_hash=hash_password(request.password),
    )
    db.add(user)
    db.flush()
    role_names = request.roles or [DEFAULT_ROLE]
    roles = list(db.scalars(select(Role).where(Role.name.in_(role_names))))
    if len(roles) != len(set(role_names)):
        raise ValueError("unknown role")
    for role in roles:
        db.execute(user_roles.insert().values(user_id=user.id, role_id=role.id))
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, tenant_id: str, user: User, request: UserUpdateRequest) -> User:
    if user.tenant_id != tenant_id:
        raise AuthenticationError("resource not found")
    if request.display_name is not None:
        user.display_name = request.display_name
    if request.active is not None:
        user.active = request.active
    if request.roles is not None:
        roles = list(db.scalars(select(Role).where(Role.name.in_(request.roles))))
        if len(roles) != len(set(request.roles)):
            raise ValueError("unknown role")
        db.execute(delete(user_roles).where(user_roles.c.user_id == user.id))
        for role in roles:
            db.execute(user_roles.insert().values(user_id=user.id, role_id=role.id))
    db.commit()
    db.refresh(user)
    return user


def permissions_for(db: Session, user_id: str) -> set[str]:
    return set(db.scalars(
        select(Permission.name)
        .join(role_permissions, role_permissions.c.permission_id == Permission.id)
        .join(user_roles, user_roles.c.role_id == role_permissions.c.role_id)
        .where(user_roles.c.user_id == user_id)
    ))


def user_response(db: Session, user: User) -> dict:
    return {
        "id": user.id,
        "tenant_id": user.tenant_id,
        "email": user.email,
        "display_name": user.display_name,
        "active": user.active,
        "roles": _roles(db, user.id),
    }