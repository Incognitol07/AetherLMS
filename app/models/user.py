# app/models/user.py

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
from .notification import Notification
from .payment import Payment

class User(Base):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(Enum('student', 'instructor', 'admin', name='user_roles'),default='student', nullable=False)
    date_joined = Column(DateTime, default=datetime.now())
    
    students = relationship("Student", back_populates="user", uselist=False)
    instructors = relationship("Instructor", back_populates="user", uselist=False)
    notifications = relationship("Notification", back_populates="user")
    discussions = relationship("Discussion", back_populates="user")
    comments = relationship("Comment", back_populates="user")
    payments = relationship("Payment", back_populates="user")

    def add_notification(self, notification: Notification):
        """Add a notification for the user."""
        self.notifications.append(notification)

    def add_payment(self, payment: Payment):
        """Add a payment made by the user."""
        self.payments.append(payment)

    def get_full_name(self):
        """Return the user's full name."""
        return self.full_name
