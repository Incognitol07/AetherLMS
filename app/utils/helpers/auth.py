#app/utils/helpers/auth.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import User, Student, Instructor
from app.schemas.auth import UserCreate
from app.utils import hash_password
from uuid import UUID

async def get_by_email(db: AsyncSession, email: str) -> User | None:
    """
    Fetch a user by their email address.

    Args:
        db (AsyncSession): The database session.
        email (str): The email address of the user.

    Returns:
        User | None: The user object if found, otherwise None.
    """
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalars().first()

async def create_user(db: AsyncSession, user: UserCreate) -> User:
    """
    Create a new user in the database.

    Args:
        db (AsyncSession): The database session.
        user (UserCreate): The user data to create.

    Returns:
        User: The newly created user object.
    """
    hashed_password = hash_password(user.password)
    db_user = User(full_name=user.full_name,email=user.email, hashed_password=hashed_password, role=user.role)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def create_student(db: AsyncSession, user_id: UUID):
    """
    Create a new user in the database.

    Args:
        db (AsyncSession): The database session.
        user_id (UUID): The user id to create.

    Returns:
        User: The newly created user object.
    """
    db_student = Student(id=user_id)
    db.add(db_student)
    await db.commit()
    await db.refresh(db_student)
    return db_student

async def create_instructor(db: AsyncSession, user_id: UUID):
    """
    Create a new user in the database.

    Args:
        db (AsyncSession): The database session.
        user_id (UUID): The user id to create.

    Returns:
        User: The newly created user object.
    """
    db_instructor = Instructor(id=user_id)
    db.add(db_instructor)
    await db.commit()
    await db.refresh(db_instructor)
    return db_instructor