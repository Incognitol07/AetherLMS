#app/utils/helpers/auth.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User
from app.schemas.auth import UserCreate

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
    db_user = User(email=user.email, hashed_password=user.hashed_password, role=user.role)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user
