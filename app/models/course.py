# app/models/course.py

import uuid
from sqlalchemy import Column, String, Text, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
from .association_tables import course_instructors  # Import from the new file
from .module import Module

class Course(Base):
    __tablename__ = "courses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(Text)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    status = Column(Enum("active", "completed", "archived", name="course_status"), default="active")

    # Many-to-Many Relationship with Instructors (using string-based reference)
    instructors = relationship("Instructor", secondary=course_instructors, back_populates="courses")
    
    # Other relationships
    modules = relationship("Module", back_populates="course")
    assignments = relationship("Assignment", back_populates="course")
    discussions = relationship("Discussion", back_populates="course")
    payments = relationship("Payment", back_populates="course")

    def add_instructor(self, instructor: "Instructor"): # type: ignore
        """Add an instructor to the course."""
        self.instructors.append(instructor)

    def remove_instructor(self, instructor: "Instructor"): # type: ignore
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