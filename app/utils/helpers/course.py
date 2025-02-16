# app/utils/helpers/course.py

from fastapi import HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models import Course, Student, Instructor, User
from uuid import UUID




async def get_course_by_title(db: AsyncSession, title: str) -> Course | None:
    """
    Fetch a course by its title.

    Args:
        db (AsyncSession): The database session.
        title (str): The title of the course.

    Returns:
        User | None: The user object if found, otherwise None.
    """
    result = await db.execute(
        select(Course)
        .filter(Course.title == title)
        )
    return result.scalar_one_or_none()



async def get_course_by_id(db: AsyncSession, id: UUID) -> Course | None:
    """
    Fetch a course by its title.

    Args:
        db (AsyncSession): The database session.
        title (str): The title of the course.

    Returns:
        User | None: The user object if found, otherwise None.
    """
    result = await db.execute(
        select(Course)
        .options(
            selectinload(Course.assignments),
            selectinload(Course.payments),
            selectinload(Course.modules),
            selectinload(Course.discussions),
            selectinload(Course.enrollments),
            selectinload(Course.instructors)
            )
        .filter(Course.id == id)
        )
    return result.scalar_one_or_none()


async def get_instructor_by_id(db: AsyncSession, id: UUID) -> Instructor | None:
    """
    Fetch a user by their email address.

    Args:
        db (AsyncSession): The database session.
        email (str): The email address of the user.

    Returns:
        User | None: The user object if found, otherwise None.
    """
    result = await db.execute(select(Instructor).options(selectinload(Instructor.courses)).filter(Instructor.id == id))
    return result.scalar_one_or_none()


async def validate_course_owner(db: AsyncSession, course_id: UUID, user: User) -> Course:
    course = await get_course_by_id(db, course_id)

    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    
    if user.id not in [i.id for i in course.instructors]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to modify this course")
    
    return course