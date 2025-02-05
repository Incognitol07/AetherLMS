# app/models/instructor.py
from sqlalchemy import Column, String, ForeignKey, DateTime, Text, JSON, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from .association_tables import course_instructors
from enum import Enum as PyEnum

class InstructorAvailability(str, PyEnum):
    ACTIVE = "active"
    ON_LEAVE = "on_leave"
    SABBATICAL = "sabbatical"
    PART_TIME = "part_time"

class Instructor(Base):
    __tablename__ = 'instructors'
    id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete="CASCADE"), primary_key=True)
    specialization = Column(String(100))
    bio = Column(Text, comment="Instructor's professional biography")
    profile_picture_url = Column(String(255))
    office_hours = Column(String(100), comment="Scheduled office hours")
    qualifications = Column(JSON, comment="List of degrees/certifications")
    availability_status = Column(Enum(InstructorAvailability), default=InstructorAvailability.ACTIVE)
    joined_at = Column(DateTime, default=func.now())
    last_accessed_at = Column(DateTime, onupdate=func.now())
    
    user = relationship("User", back_populates="instructors")
    courses = relationship("Course", secondary=course_instructors, back_populates="instructors")
    
    def add_course(self, course: "Course"): # type: ignore
        """Assign a course to the instructor."""
        if course not in self.courses:
            self.courses.append(course)

    def remove_course(self, course: "Course"): # type: ignore
        """Remove a course from the instructor."""
        if course in self.courses:
            self.courses.remove(course)

    def current_course_load(self):
        """Get number of active courses"""
        return len([c for c in self.courses if c.status == 'active'])

    def get_qualifications(self):
        """Return formatted qualifications string"""
        return ", ".join(self.qualifications) if self.qualifications else ""