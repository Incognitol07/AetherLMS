# app/models/user.py

from sqlalchemy import Column, String, Text, ForeignKey, DateTime, Float, Boolean, Enum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base
from .lesson import Lesson


class Module(Base):
    __tablename__ = 'modules'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID(as_uuid=True), ForeignKey('courses.id'))
    title = Column(String, nullable=False)
    description = Column(Text)
    order = Column(Float)
    
    course = relationship("Course", back_populates="modules")
    lessons = relationship("Lesson", back_populates="module")

    def add_lesson(self, lesson: Lesson):
        """Add a lesson to the module."""
        self.lessons.append(lesson)

    def get_lesson_count(self):
        """Get the total number of lessons in the module."""
        return len(self.lessons)
