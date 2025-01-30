# app/models/course.py

import uuid
from sqlalchemy import Column, String, Text, ForeignKey, DateTime, Enum, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
from .instructor import Instructor
from .module import Module

# Association Table for Many-to-Many Relationship
course_instructors = Table(
    "course_instructors",
    Base.metadata,
    Column("course_id", UUID(as_uuid=True), ForeignKey("courses.id"), primary_key=True),
    Column("instructor_id", UUID(as_uuid=True), ForeignKey("instructors.id"), primary_key=True)
)

class Course(Base):
    __tablename__ = "courses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(Text)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    status = Column(Enum("active", "completed", "archived", name="course_status"), default="active")

    # Many-to-Many Relationship with Instructors
    instructors = relationship("Instructor", secondary=course_instructors, back_populates="courses")
    
    # Other relationships
    modules = relationship("Module", back_populates="course")
    assignments = relationship("Assignment", back_populates="course")
    discussions = relationship("Discussion", back_populates="course")
    payments = relationship("Payment", back_populates="course")

    def add_instructor(self, instructor: Instructor):
        """Add an instructor to the course."""
        self.instructors.append(instructor)

    def remove_instructor(self, instructor: Instructor):
        """Remove an instructor from the course."""
        self.instructors.remove(instructor)

    def add_module(self, module: Module):
        """Add a module to the course."""
        self.modules.append(module)

    def remove_module(self, module: Module):
        """Remove a module from the course."""
        self.modules.remove(module)

    def get_active_modules(self):
        """Return all active modules in the course."""
        return [module for module in self.modules if module.status == 'active']
