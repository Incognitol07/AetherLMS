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

class CourseResponse(CourseCreate):
    id: UUID
    status: CourseStatus
    enrollment_count: int 
    instructor_count: int 
