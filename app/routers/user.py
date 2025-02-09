# app/routers/user.py

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models import User, Notification, Role
from app.utils import (
    get_current_user, 
    get_current_admin, 
    logger, 
    create_user, 
    get_role_by_id, 
    get_user_by_id, 
    get_role_by_name,
    get_superadmin
    )
from app.schemas.auth import UserCreate

router = APIRouter(prefix="/users", tags=["users"])


# Create a new user (admin-only)
@router.post("/", dependencies=[Depends(get_current_admin)])
async def admin_create_user(user_data: UserCreate, role_name: str, db: AsyncSession = Depends(get_db)):
    try:
        user = await create_user(user_data, db, role_name=role_name)
        logger.info(f"User '{user.email}' created successfully.")
        return {"message": "User created successfully"}
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
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
async def get_user(user_id: UUID, db: AsyncSession = Depends(get_db)):
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
async def update_user(
    user_id: UUID, user_data: dict, db: AsyncSession = Depends(get_db)
):
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
    current_user: User = Depends(get_current_user),
):
    for key, value in user_data.items():
        setattr(current_user, key, value)
    await db.commit()
    return {"message": "Profile updated successfully"}


# Delete a user (admin-only)
@router.delete("/{user_id}", dependencies=[Depends(get_current_admin)])
async def delete_user(user_id: UUID, db: AsyncSession = Depends(get_db)):
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
async def delete_my_account(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    await db.delete(current_user)
    await db.commit()
    return {"message": "Account deleted successfully"}


# Update a user's role (admin-only)
@router.put("/{user_id}/role")
async def update_user_role(
    user_id: UUID,
    role_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    role = await get_role_by_id(db,role_id)
    if role.name == "superadmin":
        if current_user.admin_info.user.role.value != "superadmin":
            return
    
    user = await get_user_by_id(db, user_id)
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
async def get_user_role(
    role_name: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_superadmin),
):
    role = await get_role_by_name(db,role_name)

    result = await db.execute(select(User).filter(User.role==role))
    users = result.scalars().all()
    return users


# Add a notification for a specific user (admin-only)
@router.post("/{user_id}/notifications", dependencies=[Depends(get_current_admin)])
async def add_user_notification(
    user_id: UUID, notification_data: dict, db: AsyncSession = Depends(get_db)
):
    user = await get_user_by_id(db, user_id)
    if not user:
        logger.warning(f"User with ID '{user_id}' not found.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    notification = Notification(**notification_data)
    user.add_notification(notification)
    await db.commit()
    return {"message": "Notification added successfully"}
