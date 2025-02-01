# app/models/background_task.py

import uuid
import json
from datetime import datetime
from app.database import Base
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Text, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func

class BackgroundTask(Base):
    __tablename__ = 'background_tasks'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_type = Column(Enum(
        'assignment_reminder', 
        'submission_processing',
        'grade_calculation',
        'bulk_enrollment',
        'progress_report',
        'content_update',
        'notification_digest',
        'video_processing',
        'data_export',
        'plagiarism_check',
        name='task_types'
    ), nullable=False)
    
    scheduled_time = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum(
        'pending', 
        'processing', 
        'completed', 
        'failed',
        name='task_status'
    ), default='pending')
    
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    course_id = Column(UUID(as_uuid=True), ForeignKey('courses.id'))
    assignment_id = Column(UUID(as_uuid=True), ForeignKey('assignments.id'))
    
    parameters = Column(JSONB, comment="Task-specific parameters in JSON format")
    result = Column(Text, comment="Task execution result or error message")
    retries = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    created_at = Column(DateTime, default=func.now)
    updated_at = Column(DateTime, default=func.now, onupdate=func.now)