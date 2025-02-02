# app/models/background_task.py

import uuid
from app.database import Base
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Text, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from enum import Enum as PyEnum

class BackgroundTaskType(str, PyEnum):
    ASSIGNMENT='assignment_reminder'
    SUBMISSION='submission_processing'
    GRADE='grade_calculation'
    ENROLLMENT='bulk_enrollment'
    PROGRESS_REPORT='progress_report'
    COURSE_DATA='course_data'
    DATA_BACKUP='data_backup'
    PLAGIARISM='plagiarism_check'
    DATA_CLEANUP='data_cleanup'

class BackgroundTask(Base):
    __tablename__ = 'background_tasks'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_type = Column(Enum(BackgroundTaskType, name='task_types'), nullable=False)
    
    scheduled_time = Column(DateTime, default=func.now)
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
    
    parameters = Column(JSON, comment="Task-specific parameters in JSON format")
    result = Column(Text, comment="Task execution result or error message")
    retries = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    created_at = Column(DateTime, default=func.now)
    updated_at = Column(DateTime, default=func.now, onupdate=func.now)