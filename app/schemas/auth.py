from pydantic import BaseModel, EmailStr
from uuid import UUID
from app.models import UserRole

class Token(BaseModel):
    access_token: str
    token_type: str


class LoginResponse(Token):
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