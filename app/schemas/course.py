from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from uuid import UUID
from app.models import CourseStatus

class CourseCreate(BaseModel):
    title: str
    description: str
    is_free: bool = True
    duration_days: Optional[int] = None

class CourseResponse(BaseModel):
    id: UUID
    title: str
    description: str | None
    status: CourseStatus
    duration_days: int | None
    enrollment_count: int
    instructor_count: int
    is_free: bool
    created_at: datetime

    class Config:
        from_attributes = True  # Enable ORM mode


class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_free: Optional[bool] = None
    duration_days: Optional[int] = None