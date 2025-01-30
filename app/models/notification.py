# app/models/notification.py

from sqlalchemy import Column, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base


class Notification(Base):
    __tablename__ = 'notifications'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    message = Column(Text)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now())
    
    user = relationship("User", back_populates="notifications")

    def mark_as_read(self):
        """Mark the notification as read."""
        self.is_read = True

    def mark_as_unread(self):
        """Mark the notification as unread."""
        self.is_read = False

