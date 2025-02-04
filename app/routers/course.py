# app/routers/course.py

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models import Course, Instructor
from app.utils import (
    get_current_instructor, 
    get_current_user, 
    logger
    )

router = APIRouter(prefix="/courses", tags=["courses"])


@router.post("/")
async def create_course(
    course_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: Instructor = Depends(get_current_instructor),
):
    try:
        course = Course(**course_data)
        db.add(course)
        await db.commit()
        logger.info(
            f"Course '{course.title}' created by instructor '{current_user.email}'."
        )
        return {"message": "Course created successfully"}
    except Exception as e:
        logger.error(f"Error creating course: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/{course_id}")
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
