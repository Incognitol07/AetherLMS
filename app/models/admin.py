# app/models/admin.py

import uuid
from sqlalchemy import Column, ForeignKey, DateTime, func, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.permission import Permission

class Role(Base):
    """
    Represents admin sub-roles and their permissions.
    """
    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(50), unique=True, nullable=False, comment="Role name (e.g., superadmin, moderator)")
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

    # Relationship to Users and Admins
    users = relationship("User", back_populates="role")  # NEW: Links users to roles

    # Relationship to Permissions (many-to-many)
    permissions = relationship("Permission", secondary="role_permission", back_populates="roles")

    def __init__(self, name: str):
        """Initialize a new role."""
        self.name = name

    def add_permission(self, permission: Permission):
        """Add a permission to the role."""
        if permission not in self.permissions:
            self.permissions.append(permission)

    def remove_permission(self, permission: Permission):
        """Remove a permission from the role."""
        if permission in self.permissions:
            self.permissions.remove(permission)

    def has_permission(self, permission_name: str) -> bool:
        """Check if the role has a specific permission."""
        return any(perm.name == permission_name for perm in self.permissions)



class Admin(Base):
    __tablename__ = "admins"

    id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, unique=True, index=True, comment="Unique reference to the user account")
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="admin_info")

    def has_permission(self, permission_name: str) -> bool:
        """Check if the admin's role has a specific permission."""
        return self.user.role and self.user.role.has_permission(permission_name)