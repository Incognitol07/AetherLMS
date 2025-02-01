from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User
from app.models.admin import Role, Admin
from app.utils.security import verify_access_token
from app.utils.helpers.auth import get_by_email
from app.utils import logger

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> User:
    """
    Retrieves the current authenticated user by verifying the provided token.

    Args:
        token (str): The authentication token passed in the Authorization header.
        db (AsyncSession): The database session to query user information.

    Raises:
        HTTPException: If token validation fails or the user cannot be found.

    Returns:
        User: The authenticated user object from the database.
    """
    try:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        # Verify the token and retrieve user information
        payload = verify_access_token(token)
        if payload is None:
            logger.warning("Token validation failed for a request.")
            raise credentials_exception

        user_email: str = payload.get("sub")
        if user_email is None:
            logger.error("Invalid token payload: Missing 'sub' field.")
            raise credentials_exception

        # Query the user by email from the database
        db_user = await get_by_email(db, user_email)
        if db_user is None:
            logger.warning(f"Unauthorized access attempt by unknown user '{user_email}'.")
            raise credentials_exception

        logger.info(f"User '{user_email}' authenticated successfully.")
        return db_user
    except Exception as e:
        logger.error(f"Error during user authentication: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during authentication",
        )

async def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Ensures the current user is an admin.

    Args:
        current_user (User): The authenticated user object.

    Raises:
        HTTPException: If the user is not an admin.

    Returns:
        User: The authenticated admin user object.
    """
    if current_user.role != "admin":
        logger.warning(f"Unauthorized admin access attempt by user '{current_user.email}'.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource",
        )
    return current_user

async def get_current_instructor(current_user: User = Depends(get_current_user)) -> User:
    """
    Ensures the current user is an instructor.

    Args:
        current_user (User): The authenticated user object.

    Raises:
        HTTPException: If the user is not an instructor.

    Returns:
        User: The authenticated instructor user object.
    """
    if current_user.role != "instructor":
        logger.warning(f"Unauthorized instructor access attempt by user '{current_user.email}'.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource",
        )
    return current_user

async def get_current_student(current_user: User = Depends(get_current_user)) -> User:
    """
    Ensures the current user is a student.

    Args:
        current_user (User): The authenticated user object.

    Raises:
        HTTPException: If the user is not a student.

    Returns:
        User: The authenticated student user object.
    """
    if current_user.role != "student":
        logger.warning(f"Unauthorized student access attempt by user '{current_user.email}'.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource",
        )
    return current_user

async def get_admin_with_permission(permission: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_admin)) -> Admin:
    """
    Ensures the current admin has a specific permission.

    Args:
        permission (str): The permission to check.
        db (AsyncSession): The database session.
        current_user (User): The authenticated admin user object.

    Raises:
        HTTPException: If the admin does not have the required permission.

    Returns:
        Admin: The authenticated admin user object with the required permission.
    """
    admin = await db.execute(
        select(Admin).filter(Admin.user_id == current_user.id)
    )
    admin = admin.scalars().first()

    if not admin or not admin.has_permission(permission):
        logger.warning(f"Unauthorized access attempt by admin '{current_user.email}' for permission '{permission}'.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You do not have permission to {permission}",
        )
    return admin

async def get_superadmin(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_admin)) -> Admin:
    """
    Ensures the current admin is a superadmin.

    Args:
        db (AsyncSession): The database session.
        current_user (User): The authenticated admin user object.

    Raises:
        HTTPException: If the admin is not a superadmin.

    Returns:
        Admin: The authenticated superadmin user object.
    """
    admin = await db.execute(
        select(Admin).filter(Admin.user_id == current_user.id)
    )
    admin = admin.scalars().first()

    if not admin or not admin.role or admin.role.name != "superadmin":
        logger.warning(f"Unauthorized superadmin access attempt by admin '{current_user.email}'.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource",
        )
    return admin

async def get_moderator(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_admin)) -> Admin:
    """
    Ensures the current admin is a moderator.

    Args:
        db (AsyncSession): The database session.
        current_user (User): The authenticated admin user object.

    Raises:
        HTTPException: If the admin is not a moderator.

    Returns:
        Admin: The authenticated moderator user object.
    """
    admin = await db.execute(
        select(Admin).filter(Admin.user_id == current_user.id)
    )
    admin = admin.scalars().first()

    if not admin or not admin.role or admin.role.name != "moderator":
        logger.warning(f"Unauthorized moderator access attempt by admin '{current_user.email}'.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource",
        )
    return admin