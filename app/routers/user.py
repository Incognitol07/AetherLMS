# app/routers/user.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models import User, Notification, UserRole
from app.utils import (
    get_current_user, 
    get_current_admin, 
    logger
)

router = APIRouter(prefix="/users", tags=["users"])

# Create a new user (admin-only)
@router.post("/", dependencies=[Depends(get_current_admin)])
async def create_user(user_data: dict, db: AsyncSession = Depends(get_db)):
    try:
        user = User(**user_data)
        db.add(user)
        await db.commit()
        logger.info(f"User '{user.email}' created successfully.")
        return {"message": "User created successfully"}
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )

# Get all users (admin-only)
@router.get("/", dependencies=[Depends(get_current_admin)])
async def get_all_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return users

# Get current user's profile
@router.get("/me")
async def get_my_profile(current_user: User = Depends(get_current_user)):
    return current_user

# Get a specific user's details (admin-only)
@router.get("/{user_id}", dependencies=[Depends(get_current_admin)])
async def get_user(user_id: str, db: AsyncSession = Depends(get_db)):
    user = await db.execute(select(User).where(User.id == user_id))
    user = user.scalar_one_or_none()
    if not user:
        logger.warning(f"User with ID '{user_id}' not found.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user

# Update a user's details (admin-only)
@router.put("/{user_id}", dependencies=[Depends(get_current_admin)])
async def update_user(user_id: str, user_data: dict, db: AsyncSession = Depends(get_db)):
    user = await db.execute(select(User).where(User.id == user_id))
    user = user.scalar_one_or_none()
    if not user:
        logger.warning(f"User with ID '{user_id}' not found.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    for key, value in user_data.items():
        setattr(user, key, value)
    await db.commit()
    return {"message": "User updated successfully"}

# Update current user's profile
@router.put("/me")
async def update_my_profile(
    user_data: dict, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_user)
    ):
    for key, value in user_data.items():
        setattr(current_user, key, value)
    await db.commit()
    return {"message": "Profile updated successfully"}

# Delete a user (admin-only)
@router.delete("/{user_id}", dependencies=[Depends(get_current_admin)])
async def delete_user(user_id: str, db: AsyncSession = Depends(get_db)):
    user = await db.execute(select(User).where(User.id == user_id))
    user = user.scalar_one_or_none()
    if not user:
        logger.warning(f"User with ID '{user_id}' not found.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    await db.delete(user)
    await db.commit()
    return {"message": "User deleted successfully"}

# Delete current user's account
@router.delete("/me")
async def delete_my_account(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    await db.delete(current_user)
    await db.commit()
    return {"message": "Account deleted successfully"}

# Update a user's role (admin-only)
@router.put("/{user_id}/role")
async def update_user_role(user_id: str, role: UserRole, db: AsyncSession = Depends(get_db), current_admin:User = Depends(get_current_admin)):
    if role == UserRole.ADMIN:
        if current_admin.admin_info.role.value!="superadmin":
            return

    user = await db.execute(select(User).where(User.id == user_id))
    user = user.scalar_one_or_none()
    if not user:
        logger.warning(f"User with ID '{user_id}' not found.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    user.role = role
    await db.commit()
    return {"message": "User role updated successfully"}

# List users by role (admin-only)
@router.get("/role/{role}")
async def get_user_role( role: UserRole, db: AsyncSession = Depends(get_db), current_admin:User = Depends(get_current_admin)):
    if role == UserRole.ADMIN:
        if current_admin.admin_info.role.name!="superadmin":
            return

    result = await db.execute(select(User).where(User.role == role))
    users = result.scalars().all()
    return users

# Add a notification for a specific user (admin-only)
@router.post("/{user_id}/notifications", dependencies=[Depends(get_current_admin)])
async def add_user_notification(user_id: str, notification_data: dict, db: AsyncSession = Depends(get_db)):
    user = await db.execute(select(User).where(User.id == user_id))
    user = user.scalar_one_or_none()
    if not user:
        logger.warning(f"User with ID '{user_id}' not found.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    notification = Notification(**notification_data)
    user.notifications.append(notification)
    await db.commit()
    return {"message": "Notification added successfully"}