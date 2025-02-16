# app/routers/course.py

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models import Course, User, Module
from app.utils import (
    get_current_instructor, 
    get_course_by_title,
    get_course_by_id,
    get_instructor_by_id,
    logger
    )
from app.schemas import (
    CourseCreate, 
    CourseResponse,
    CourseUpdate,
    ModuleResponse,
    ModuleCreate
    )
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


@router.put("/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: UUID,
    course_data: CourseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_instructor),
):
    try:
        
        # Get existing course
        course = await get_course_by_id(db, course_id)
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")

        # Authorization check
        if current_user.id not in [instructor.id for instructor in course.instructors]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to modify this course")

        update_data = course_data.model_dump(exclude_unset=True)

        # Check for title conflict (if title is being updated)
        if "title" in update_data:
            new_title = update_data["title"]
            
            # Check against other courses excluding current one
            stmt = select(Course).where(
                Course.title == new_title,
                Course.id != course_id  # Exclude current course from check
            )
            result = await db.execute(stmt)
            conflicting_course = result.scalar_one_or_none()
            
            if conflicting_course:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Course title already exists"
                )

        # Apply updates
        for key, value in update_data.items():
            setattr(course, key, value)

        await db.commit()
        await db.refresh(course)
        
        logger.info(f"Course '{course.id}' updated by instructor '{current_user.email}'.")
        return course

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating course: {e}")
        await db.rollback()
        raise HTTPException(500, "Internal server error")

@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
    course_id: UUID, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_instructor),
):
    try:
        # 1. Check if course exists first
        course = await get_course_by_id(db, course_id)
        if not course:
            logger.warning(f"Course with ID '{course_id}' not found.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Course not found"
            )

        # 2. Check authorization after existence check
        if current_user.id not in [instructor.id for instructor in course.instructors]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to modify this course"
            )

        # 3. Perform deletion
        await db.delete(course)
        await db.commit()  # Fixed missing parentheses

    except HTTPException:
        # Let specific HTTP exceptions bubble up
        raise
    except Exception as e:
        logger.error(f"Error deleting course: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/{course_id}/modules", response_model=ModuleResponse)
async def create_module(
    course_id: UUID,
    module_data: ModuleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_instructor),
):
    try:
        course = await get_course_by_id(db, course_id)
        if not course:
            logger.warning(f"Course with ID '{course_id}' not found.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Course not found"
            )
        
        if current_user.id not in [instructor.id for instructor in course.instructors]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to modify this course"
            )
        
        new_module = Module(**module_data.model_dump(), course_id=course.id)
        db.add(new_module)
        await db.commit()
        await db.refresh(new_module)
        logger.info(
            f"Course '{new_module.title}' created by instructor '{current_user.email}'."
        )
        return new_module
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating course: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )