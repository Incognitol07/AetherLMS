# app/models/user.py

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.database import Base
from sqlalchemy.sql import func
from enum import Enum as PyEnum

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id", ondelete="SET NULL"), nullable=True)
    date_joined = Column(DateTime, default=func.now())

    # Define relationships
    role = relationship("Role", back_populates="users")
    admin_info = relationship("Admin", back_populates="user", uselist=False, cascade="all, delete-orphan")
    students = relationship("Student", back_populates="user", uselist=False, cascade="all, delete-orphan")
    instructors = relationship("Instructor", back_populates="user", uselist=False, cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    discussions = relationship("Discussion", back_populates="user", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="user", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="user", cascade="all, delete-orphan")

    def assign_role(self, role: "Role"): # type: ignore
        """Assign a role to the user."""
        self.role = role

    def has_permission(self, permission_name: str) -> bool:
        """Check if the user's role has a specific permission."""
        return self.role and self.role.has_permission(permission_name)

    def add_notification(self, notification: "Notification"): # type: ignore
        """Add a notification for the user."""
        self.notifications.append(notification)

    def add_payment(self, payment: "Payment"): # type: ignore
        """Add a payment made by the user."""
        self.payments.append(payment)