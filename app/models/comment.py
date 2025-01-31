# app/models/comment.py

import uuid
from sqlalchemy import Column, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Comment(Base):
    __tablename__ = 'comments'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    discussion_id = Column(UUID(as_uuid=True), ForeignKey('discussions.id'))
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    content = Column(Text)
    created_at = Column(DateTime, default=func.now())
    
    discussion = relationship("Discussion", back_populates="comments")
    user = relationship("User", back_populates="comments")

    def edit_content(self, new_content: str):
        """Edit the content of the comment."""
        self.content = new_content

    def get_author(self):
        """Return the user who authored the comment."""
        return self.user.full_name
