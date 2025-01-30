# app/models/discussion.py

from sqlalchemy import Column, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base
from .comment import Comment

class Discussion(Base):
    __tablename__ = 'discussions'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID(as_uuid=True), ForeignKey('courses.id'))
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.now())
    
    course = relationship("Course", back_populates="discussions")
    user = relationship("User", back_populates="discussions")
    comments = relationship("Comment", back_populates="discussion")

    def add_comment(self, comment: Comment):
        """Add a comment to the discussion."""
        self.comments.append(comment)

    def get_discussion_content(self):
        """Return the content of the discussion."""
        return self.content
