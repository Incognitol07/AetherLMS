# app/models/admin.py

import uuid
from sqlalchemy import Column, ForeignKey, JSON, DateTime, func, String, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class Role(Base):
    """
    Represents different admin roles with specific permissions.
    """
    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(50), unique=True, nullable=False, comment="Role name (e.g., superadmin, moderator)")
    permissions = Column(JSON, nullable=False, default=list, comment="Permissions assigned to the role")
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

    # Relationship to Admins who have this role
    admins = relationship("Admin", back_populates="role")

    # Predefined default roles and permissions
    ROLE_DEFAULT_PERMISSIONS = {
        "admin": ["view_reports", "manage_users"],
        "superadmin": ["view_reports", "manage_users", "edit_settings", "delete_data"],
        "moderator": ["view_reports"]
    }

    def __init__(self, name: str, permissions=None):
        """
        Automatically assigns default permissions if none are provided.
        """
        self.name = name
        self.permissions = permissions or self.ROLE_DEFAULT_PERMISSIONS.get(name, [])

    def add_permission(self, permission: str):
        """Add a new permission to the role."""
        if permission not in self.permissions:
            self.permissions.append(permission)

    def remove_permission(self, permission: str):
        """Remove a permission from the role."""
        if permission in self.permissions:
            self.permissions.remove(permission)

    def has_permission(self, permission: str) -> bool:
        """Check if the role has a specific permission."""
        return permission in self.permissions


class Admin(Base):
    """
    Represents additional information specific to admins, linking them to roles.
    """
    __tablename__ = "admins"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True, comment="Unique reference to the user account")
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id", ondelete="SET NULL"), nullable=True, comment="Reference to the assigned role")
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="admin_info")
    role = relationship("Role", back_populates="admins")

    def assign_role(self, role: Role):
        """Assign a role to the admin."""
        self.role = role

    def has_permission(self, permission: str) -> bool:
        """Check if the admin's role has a specific permission."""
        return self.role and permission in self.role.permissions
