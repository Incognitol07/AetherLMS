# app/routers/user.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models import User
from app.utils import (
    get_current_user, 
    logger
    )

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/")
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


@router.get("/{user_id}")
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = await db.execute(select(User).where(User.id == user_id))
    user = user.scalar_one_or_none()
    if not user:
        logger.warning(f"User with ID '{user_id}' not found.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


# Add other user endpoints (PUT /users/{user_id}, DELETE /users/{user_id}, etc.)
