# app/utils/helpers/auth.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models import User, Student, Instructor, Admin, Role
from app.schemas.auth import UserCreate
from app.utils import hash_password
from uuid import UUID
from app.utils import logger


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """
    Fetch a user by their email address.

    Args:
        db (AsyncSession): The database session.
        email (str): The email address of the user.

    Returns:
        User | None: The user object if found, otherwise None.
    """
    result = await db.execute(select(User).options(selectinload(User.role)).filter(User.email == email))
    return result.scalars().first()


async def get_user_by_id(db: AsyncSession, id: UUID) -> User | None:
    """
    Fetch a user by their email address.

    Args:
        db (AsyncSession): The database session.
        email (str): The email address of the user.

    Returns:
        User | None: The user object if found, otherwise None.
    """
    result = await db.execute(select(User).filter(User.id == id))
    return result.scalars().first()


async def get_role_by_name(db: AsyncSession, name: str) -> Role | None:
    """
    Fetch a role by its name.

    Args:
        db (AsyncSession): The database session.
        name (name): The name of the role.

    Returns:
        User | None: The user object if found, otherwise None.
    """
    result = await db.execute(select(Role).filter(Role.name == name))
    return result.scalars().first()


async def get_role_by_id(db: AsyncSession, id: UUID) -> Role | None:
    """
    Fetch a role by its id.

    Args:
        db (AsyncSession): The database session.
        id (UUID): The id of the role.

    Returns:
        User | None: The user object if found, otherwise None.
    """
    result = await db.execute(select(Role).options(selectinload(Role.permissions)).filter(Role.id == id))
    return result.scalars().first()


async def get_admin_by_id(db: AsyncSession, id: UUID) -> Admin | None:
    """
    Fetch an admin by their user ID.

    Args:
        db (AsyncSession): The database session
        id (UUID): The user ID of the admin

    Returns:
        Admin | None: Admin record if found
    """
    result = await db.execute(
        select(Admin)
        .options(selectinload(Admin.user).selectinload(User.role))
        .filter(Admin.id == id)
    )
    return result.scalar()


async def create_user(
    db: AsyncSession, 
    user: UserCreate, 
    role_name: str
) -> User:
    """
    Create a new user in the database.

    Args:
        db (AsyncSession): The database session.
        user (UserCreate): The user data to create.
        role_name(str): The name of the role of the user

    Returns:
        User: The newly created user object.
    """
    try:
        role = await get_role_by_name(db=db,name=role_name)
        if not role:
            raise Exception("Role does not exist")
        hashed_password = hash_password(user.password)
        db_user = User(
            full_name=user.full_name,
            email=user.email,
            hashed_password=hashed_password,
            role_id=role.id,
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user
    except Exception as e:
        await db.rollback()
        logger.error(f"User creation failed: {str(e)}")
        raise


async def create_student(db: AsyncSession, user_id: UUID) -> Student:
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


async def create_instructor(db: AsyncSession, user_id: UUID) -> Instructor:
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
