# app/models/permission.py

import uuid
from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base

class Permission(Base):
    """
    Represents individual permissions that can be assigned to roles.
    """
    __tablename__ = "permissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(50), unique=True, nullable=False, comment="Permission name (e.g., view_reports, manage_users)")
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

    # Relationship to Roles (many-to-many)
    roles = relationship("Role", secondary="role_permission", back_populates="permissions")