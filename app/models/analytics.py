# app/models/analytics.py

import uuid
from datetime import datetime
from sqlalchemy import Column, ForeignKey, DateTime, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Analytics(Base):
    __tablename__ = 'analytics'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID(as_uuid=True), ForeignKey('courses.id'))
    student_id = Column(UUID(as_uuid=True), ForeignKey('students.id'))
    completion_rate = Column(Float)
    last_active = Column(DateTime, default=func.now())
    
    course = relationship("Course")
    student = relationship("Student", back_populates="analytics")

    def update_completion_rate(self, new_rate: float):
        """Update the student's completion rate."""
        self.completion_rate = new_rate

    def set_last_active(self, last_active: datetime):
        """Update the last active date for the student."""
        self.last_active = last_active