# app/models/instructor.py

from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
from .association_tables import course_instructors  # Import from the new file

class Instructor(Base):
    __tablename__ = 'instructors'
    id = Column(UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True)
    specialization = Column(String)
    user = relationship("User", back_populates="instructors")

    # Many-to-Many Relationship with Courses (using string-based reference)
    courses = relationship("Course", secondary=course_instructors, back_populates="instructors")

    def add_course(self, course: "Course"): # type: ignore
        """Assign a course to the instructor."""
        self.courses.append(course)

    def remove_course(self, course: "Course"): # type: ignore
        """Remove a course from the instructor."""
        self.courses.remove(course)