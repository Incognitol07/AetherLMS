# app/models/association_tables.py

from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base

# Association Table for Many-to-Many Relationship between Role and Permission
role_permission = Table(
    "role_permission",
    Base.metadata,
    Column("role_id", UUID(as_uuid=True), ForeignKey("roles.id"), primary_key=True),
    Column("permission_id", UUID(as_uuid=True), ForeignKey("permissions.id"), primary_key=True)
)

# Association Table for Many-to-Many Relationship between Course and Instructor
course_instructors = Table(
    "course_instructors",
    Base.metadata,
    Column("course_id", UUID(as_uuid=True), ForeignKey("courses.id"), primary_key=True),
    Column("instructor_id", UUID(as_uuid=True), ForeignKey("instructors.id"), primary_key=True)
)