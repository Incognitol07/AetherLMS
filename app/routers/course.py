# app/routers/course.py

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models import Course, Student, Instructor, User
from app.utils import (
    get_current_instructor, 
    get_course_by_title, 
    get_instructor_by_id,
    logger
    )
from app.schemas import CourseCreate, CourseResponse
from typing import List

router = APIRouter(prefix="/courses", tags=["Courses"])

@router.get("/", response_model=List[CourseResponse])
async def get_courses(db: AsyncSession = Depends(get_db)):
    course = await db.execute(select(Course))
    course = course.scalars().all()
    return course

@router.post("/", response_model=CourseResponse)
async def create_course(
    course_data: CourseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_instructor),
):
    try:
        existing_course = await get_course_by_title(db, course_data.title)
        if existing_course:
            logger.info(f"Instructor {current_user.id} tried to create a course with an existing title.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Course title already exists"
            )
        instructor = await get_instructor_by_id(db, current_user.id)
        new_course = Course(**course_data.model_dump())  # Convert to dictionary
        new_course.add_instructor(instructor)
        db.add(new_course)
        await db.commit()
        await db.refresh(new_course)
        logger.info(
            f"Course '{new_course.title}' created by instructor '{current_user.email}'."
        )
        return new_course
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating course: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/{course_id}", response_model=CourseResponse)
async def get_course(course_id: UUID, db: AsyncSession = Depends(get_db)):
    course = await db.execute(select(Course).where(Course.id == course_id))
    course = course.scalar_one_or_none()
    if not course:
        logger.warning(f"Course with ID '{course_id}' not found.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
        )
    return course



# Add other course endpoints (PUT /courses/{course_id}, DELETE /courses/{course_id}, etc.)
