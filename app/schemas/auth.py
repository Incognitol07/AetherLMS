from pydantic import BaseModel, EmailStr
from uuid import UUID
from app.models import UserRole

class Token(BaseModel):
    access_token: str
    token_type: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class LoginResponse(Token):
    refresh_token: str
    scopes: list



class UserBase(BaseModel):
    email: EmailStr
    role: UserRole

class UserCreate(UserBase):
    full_name: str
    password: str

class UserResponse(UserBase):
    id: UUID

    class Config:
        from_attributes = True