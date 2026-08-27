from pydantic import BaseModel, EmailStr
import uuid

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: str | None = None
    tenant_id: str | None = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str | None = None
    last_name: str | None = None
    tenant_id: uuid.UUID
    
class UserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    first_name: str | None = None
    last_name: str | None = None
    tenant_id: uuid.UUID
    is_active: bool

    class Config:
        from_attributes = True
