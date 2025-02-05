# app/models/student.py

from sqlalchemy import Column, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
from .enrollment import EnrollmentStatus

class Student(Base):
    __tablename__ = 'students'
    id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete="CASCADE"), primary_key=True)
    progress = Column(JSON, default={})  # Stores course progress as JSON
    user = relationship("User", back_populates="students")
    submissions = relationship("Submission", back_populates="student")
    analytics = relationship("Analytics", back_populates="student")
    enrollments = relationship("Enrollment", back_populates="student")

    def add_submission(self, submission: "Submission"): # type: ignore
        """Add a submission for the student."""
        self.submissions.append(submission)

    def update_progress(self, progress_data: dict):
        """Update the student's course progress."""
        self.progress.update(progress_data)

    def get_active_enrollments(self):
        """Return all active course enrollments."""
        return [enrollment for enrollment in self.enrollments
                if enrollment.status == EnrollmentStatus.ACTIVE]
