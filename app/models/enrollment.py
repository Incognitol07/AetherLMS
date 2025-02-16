# app/models/enrollment.py
from sqlalchemy import Column, ForeignKey, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, object_session
from sqlalchemy.sql import func
import uuid
from app.database import Base
from enum import Enum as PyEnum
from datetime import timedelta

class EnrollmentStatus(str, PyEnum):
    ACTIVE = "active"
    COMPLETED = "completed"
    DROPPED = "dropped"
    SUSPENDED = "suspended"

class Enrollment(Base):
    __tablename__ = 'enrollments'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey('students.id'), nullable=False)
    course_id = Column(UUID(as_uuid=True), ForeignKey('courses.id'), nullable=False)
    enrolled_at = Column(DateTime, default=func.now())
    start_date = Column(DateTime, default=func.now())  # Track when a student starts the course
    end_date = Column(DateTime, nullable=True)  # Optional, can be set when course is completed
    status = Column(Enum(EnrollmentStatus), default=EnrollmentStatus.ACTIVE)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    student = relationship("Student", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set expected end date based on course duration
        if self.course and self.course.duration_days:
            self.end_date = self.start_date + timedelta(days=self.course.duration_days)
        if self.course:
            self.course.enrollment_count += 1

    def complete_enrollment(self):
        """Mark enrollment as completed."""
        self.status = EnrollmentStatus.COMPLETED
        self.completed_at = func.now()
        self.end_date = func.now()

    def update_status(self, new_status: EnrollmentStatus):
        """Update enrollment status with validation."""
        valid_transitions = {
            EnrollmentStatus.ACTIVE: [EnrollmentStatus.COMPLETED, EnrollmentStatus.DROPPED],
            EnrollmentStatus.SUSPENDED: [EnrollmentStatus.ACTIVE, EnrollmentStatus.DROPPED],
            EnrollmentStatus.DROPPED: [],
            EnrollmentStatus.COMPLETED: []
        }
        
        if new_status not in valid_transitions[self.status]:
            raise ValueError(f"Invalid status transition from {self.status} to {new_status}")
            
        self.status = new_status
