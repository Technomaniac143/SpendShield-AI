from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.auth import Principal, require_permission
from app.core.database import get_db
from app.models import User
from app.schemas import UserCreateRequest, UserResponse, UserUpdateRequest
from app.services import auth as auth_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserResponse])
def list_users(principal: Principal = Depends(require_permission("admin:users")), db: Session = Depends(get_db)):
    users = list(db.scalars(select(User).where(User.tenant_id == principal.tenant_id).order_by(User.email)))
    return [auth_service.user_response(db, user) for user in users]


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(request: UserCreateRequest, principal: Principal = Depends(require_permission("admin:users")), db: Session = Depends(get_db)):
    try:
        user = auth_service.create_user(db, principal.tenant_id, request)
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="email already exists") from exc
    return auth_service.user_response(db, user)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: str, principal: Principal = Depends(require_permission("admin:users")), db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.id == user_id, User.tenant_id == principal.tenant_id))
    if user is None:
        raise HTTPException(status_code=404, detail="user not found")
    return auth_service.user_response(db, user)


@router.patch("/{user_id}", response_model=UserResponse)
def update_user(user_id: str, request: UserUpdateRequest, principal: Principal = Depends(require_permission("admin:users")), db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.id == user_id, User.tenant_id == principal.tenant_id))
    if user is None:
        raise HTTPException(status_code=404, detail="user not found")
    try:
        return auth_service.user_response(db, auth_service.update_user(db, principal.tenant_id, user, request))
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: str, principal: Principal = Depends(require_permission("admin:users")), db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.id == user_id, User.tenant_id == principal.tenant_id))
    if user is None:
        raise HTTPException(status_code=404, detail="user not found")
    user.active = False
    db.commit()