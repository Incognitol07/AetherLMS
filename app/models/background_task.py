# app/models/background_task.py

import uuid
from app.database import Base
from sqlalchemy import Column, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID


class BackgroundTask(Base):
    __tablename__ = 'background_tasks'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_type = Column(Enum('assignment_reminder', 'progress_check', name='task_types'))
    scheduled_time = Column(DateTime, nullable=False)
    status = Column(Enum('pending', 'completed', 'failed', name='task_status'), default='pending')
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))  # Reference to user

    def mark_as_completed(self):
        """Mark the background task as completed."""
        self.status = 'completed'

    def mark_as_failed(self):
        """Mark the background task as failed."""
        self.status = 'failed'