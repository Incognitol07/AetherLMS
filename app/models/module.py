# app/models/user.py

from sqlalchemy import Column, String, Text, ForeignKey, Float, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.database import Base


class Module(Base):
    __tablename__ = 'modules'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID(as_uuid=True), ForeignKey('courses.id'))
    title = Column(String, nullable=False)
    description = Column(Text)
    order = Column(Float)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    
    course = relationship("Course", back_populates="modules")
    lessons = relationship("Lesson", back_populates="module")

    def add_lesson(self, lesson: "Lesson"): # type: ignore
        """Add a lesson to the module."""
        self.lessons.append(lesson)

    def get_lesson_count(self):
        """Get the total number of lessons in the module."""
        return len(self.lessons)
