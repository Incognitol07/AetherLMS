# app/models/enrollment.py
from sqlalchemy import Column, ForeignKey, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base
from enum import Enum as PyEnum

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
    status = Column(Enum(EnrollmentStatus), default=EnrollmentStatus.ACTIVE)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    student = relationship("Student", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")

    def complete_enrollment(self):
        """Mark enrollment as completed."""
        self.status = EnrollmentStatus.COMPLETED
        self.completed_at = func.now()

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