from typing import List, Optional
from datetime import date
from pydantic import BaseModel

# Instructor Schemas
class InstructorResponse(BaseModel):
    id: int  # This refers to the User ID, as Instructor is linked to User
    full_name: str
    specialization: Optional[str] = None

    class Config:
        from_attributes = True

# Module Schemas
class ModuleBase(BaseModel):
    id: int
    title: str
    order: int

    class Config:
        from_attributes = True

class ModuleCreate(BaseModel):
    title: str
    order: int
    description: Optional[str] = None

class ModuleUpdate(BaseModel):
    title: Optional[str] = None
    order: Optional[int] = None
    description: Optional[str] = None

class ModuleResponse(ModuleBase):
    description: Optional[str] = None
    course_id: int

# Lesson Schemas
class LessonBase(BaseModel):
    id: int
    title: str
    order: int

    class Config:
        from_attributes = True

class LessonCreate(BaseModel):
    title: str
    order: int
    content: Optional[str] = None

class LessonUpdate(BaseModel):
    title: Optional[str] = None
    order: Optional[int] = None
    content: Optional[str] = None

class LessonResponse(LessonBase):
    content: Optional[str] = None
    module_id: int

# Course Schemas
class CourseCreate(BaseModel):
    title: str
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = "active"

class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = None

class CourseResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    start_date: Optional[date]
    end_date: Optional[date]
    status: str
    instructors: List[InstructorResponse]
    modules: List[ModuleBase]

    class Config:
        from_attributes = True
