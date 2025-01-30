# app/models/assignment.py

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
from .submission import Submission


class Assignment(Base):
    __tablename__ = 'assignments'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID(as_uuid=True), ForeignKey('courses.id'))
    title = Column(String, nullable=False)
    description = Column(Text)
    due_date = Column(DateTime)
    file_upload_url = Column(String)
    
    course = relationship("Course", back_populates="assignments")
    submissions = relationship("Submission", back_populates="assignment")

    def add_submission(self, submission: Submission):
        """Add a submission to the assignment."""
        self.submissions.append(submission)

    def get_submission_count(self):
        """Return the total number of submissions for the assignment."""
        return len(self.submissions)

    def set_due_date(self, new_due_date: datetime):
        """Set a new due date for the assignment."""
        self.due_date = new_due_date