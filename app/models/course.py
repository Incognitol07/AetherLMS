# app/models/course.py

import uuid
from sqlalchemy import Column, String, Text, DateTime, Enum, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from .association_tables import course_instructors 
from .module import Module
from .enrollment import EnrollmentStatus
from enum import Enum as PyEnum

class CourseStatus(str, PyEnum):
    ACTIVE="active"
    COMPLETED="completed"
    ARCHIVED="archived"

class Course(Base):
    __tablename__ = "courses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(Text)
    status = Column(Enum(CourseStatus), default=CourseStatus.ACTIVE)
    duration_days = Column(Integer, nullable=True)  
    enrollment_count = Column(Integer, default=0)
    instructor_count = Column(Integer, default=0)
    is_free = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

    # Many-to-Many Relationship with Instructors (using string-based reference)
    instructors = relationship("Instructor", secondary=course_instructors, back_populates="courses")
    
    # Other relationships
    modules = relationship("Module", back_populates="course")
    assignments = relationship("Assignment", back_populates="course")
    discussions = relationship("Discussion", back_populates="course")
    payments = relationship("Payment", back_populates="course")
    enrollments = relationship("Enrollment", back_populates="course")

    def add_instructor(self, instructor: "Instructor"):  # type: ignore
        """Add an instructor to the course if not already added."""
        if instructor not in self.instructors:
            self.instructors.append(instructor)
        self.instructor_count = len(self.instructors)

    def remove_instructor(self, instructor: "Instructor"): # type: ignore
        """Remove an instructor from the course."""
        self.instructors.remove(instructor)
        self.instructor_count = len(self.instructors)

    def add_module(self, module: Module):
        """Add a module to the course."""
        self.modules.append(module)

    def remove_module(self, module: Module):
        """Remove a module from the course."""
        self.modules.remove(module)

    def get_active_modules(self):
        """Return all active modules in the course."""
        return [module for module in self.modules if module.status == 'active']
    
    def get_active_enrollments(self):
        """Return all active enrollments."""
        return [enrollment for enrollment in self.enrollments 
                if enrollment.status == EnrollmentStatus.ACTIVE]

    def get_enrollment_count(self):
        """Return total number of enrollments."""
        return len(self.enrollments)
