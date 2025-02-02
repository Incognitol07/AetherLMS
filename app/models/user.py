# app/models/user.py

import uuid
from sqlalchemy import Column, String, DateTime, Enum
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
from enum import Enum as PyEnum

# Define the primary user roles
class UserRole(str, PyEnum):
    STUDENT = "student"
    INSTRUCTOR = "instructor"
    ADMIN = "admin"

class User(Base):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.STUDENT, nullable=False)
    date_joined = Column(DateTime, default=func.now())
    
    admin_info = relationship("Admin", back_populates="user", uselist=False)
    students = relationship("Student", back_populates="user", uselist=False)
    instructors = relationship("Instructor", back_populates="user", uselist=False)
    notifications = relationship("Notification", back_populates="user")
    discussions = relationship("Discussion", back_populates="user")
    comments = relationship("Comment", back_populates="user")
    payments = relationship("Payment", back_populates="user")

    def add_notification(self, notification: "Notification"): # type: ignore
        """Add a notification for the user."""
        self.notifications.append(notification)

    def add_payment(self, payment: "Payment"): # type: ignore
        """Add a payment made by the user."""
        self.payments.append(payment)