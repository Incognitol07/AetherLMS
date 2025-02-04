# app/schemas/admin.py

from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from uuid import UUID
from .auth import UserCreate
from app.models import UserRole

# ------------------------------ Role Schemas ------------------------------

class RoleCreate(BaseModel):
    """
    Schema for creating a new role.
    """
    name: str = Field(..., description="Name of the role", example="moderator")
    permissions: List[str] = Field(
        default_factory=list,
        description="List of permissions for the role",
        example=["view_reports", "manage_users"]
    )


class RoleUpdate(BaseModel):
    """
    Schema for updating an existing role.
    """
    name: Optional[str] = Field(None, description="Name of the role", example="moderator")
    permissions: Optional[List[str]] = Field(
        None,
        description="List of permissions for the role",
        example=["view_reports", "manage_users"]
    )


class PermissionUpdate(BaseModel):
    """
    Schema for adding or removing a permission from a role.
    """
    permission: str = Field(..., description="Permission to add or remove", example="manage_users")


# ------------------------------ Admin User Schemas ------------------------------

class AdminCreate(UserCreate):
    """
    Schema for creating a new admin.
    """
    role: Optional[UserRole] = None
    admin_sub_role: str


class AdminUpdate(BaseModel):
    """
    Schema for updating an existing admin.
    """
    role_id: Optional[UUID] = Field(
        None,
        description="ID of the role to assign to the admin"
    )


# ------------------------------ Response Schemas ------------------------------

class RoleResponse(BaseModel):
    """
    Schema for returning role details.
    """
    id: UUID
    name: str
    permissions: List[str]
    created_at: str

    class Config:
        from_attributes = True  # Enable ORM mode for SQLAlchemy models


class AdminResponse(BaseModel):
    """
    Schema for returning admin details.
    """
    id: UUID
    role_id: Optional[UUID]
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True  # Enable ORM mode for SQLAlchemy models