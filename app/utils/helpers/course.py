# app/utils/helpers/course.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models import Course, Student, Instructor
from uuid import UUID
from app.utils import logger



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