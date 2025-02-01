# app/models/submission.py

from sqlalchemy import Column, String,ForeignKey, DateTime, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base


class Submission(Base):
    __tablename__ = 'submissions'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assignment_id = Column(UUID(as_uuid=True), ForeignKey('assignments.id'))
    student_id = Column(UUID(as_uuid=True), ForeignKey('students.id'))
    submission_url = Column(String)
    submitted_at = Column(DateTime, default=func.now())
    grade = Column(Float, nullable=True)
    
    assignment = relationship("Assignment", back_populates="submissions")
    student = relationship("Student", back_populates="submissions")

    def update_grade(self, grade: float):
        """Update the grade for the submission."""
        self.grade = grade

    def get_submission_status(self):
        """Return the submission status based on grade."""
        if self.grade is None:
            return "Pending"
        elif self.grade >= 50:
            return "Passed"
        return "Failed"
