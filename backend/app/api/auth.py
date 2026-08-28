from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import Principal, get_current_principal
from app.core.database import get_db
from app.models import User
from app.schemas import LoginRequest, LogoutRequest, RefreshRequest, TokenResponse, UserResponse
from app.services import auth as auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    try:
        return auth_service.login(db, request)
    except auth_service.AuthenticationError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials") from exc


@router.post("/refresh", response_model=TokenResponse)
def refresh(request: RefreshRequest, db: Session = Depends(get_db)):
    try:
        return auth_service.refresh(db, request)
    except auth_service.AuthenticationError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid refresh token") from exc


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(request: LogoutRequest, db: Session = Depends(get_db)):
    auth_service.logout(db, request)


@router.get("/me", response_model=UserResponse)
def me(principal: Principal = Depends(get_current_principal), db: Session = Depends(get_db)):
    if principal.user_id is None:
        raise HTTPException(status_code=401, detail="user session required")
    user = db.scalar(select(User).where(User.id == principal.user_id, User.tenant_id == principal.tenant_id))
    if user is None or not user.active:
        raise HTTPException(status_code=401, detail="user session required")
    return auth_service.user_response(db, user)