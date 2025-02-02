# app/models/notification.py

from sqlalchemy import Column, Text, ForeignKey, DateTime, Boolean, Enum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base
from enum import Enum as PyEnum

class NotificationType(str, PyEnum):
    ENROLLMENT = "enrollment"
    GRADE = "grade"
    COURSE_UPDATE = "course_update"
    ASSIGNMENT = "assignment"
    PAYMENT = "payment"
    SYSTEM = "system"
    DISCUSSION = "discussion"
    INSTRUCTOR = "instructor"
    DEADLINE = "deadline"
    PLAGIARISM="plagiarism"

class Notification(Base):
    __tablename__ = 'notifications'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    message = Column(Text)
    notification_type = Column(Enum(NotificationType), nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    additional_data = Column(JSON, default={})
    
    user = relationship("User", back_populates="notifications")

    def mark_as_read(self):
        """Mark the notification as read."""
        self.is_read = True

    def mark_as_unread(self):
        """Mark the notification as unread."""
        self.is_read = False