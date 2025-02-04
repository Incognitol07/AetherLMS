# app/routers/notification.py

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models import Notification, User
from app.utils import (
    get_current_user, 
    logger
    )

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/")
async def list_notifications(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    notifications = await db.execute(
        select(Notification).where(Notification.user_id == current_user.id)
    )
    return notifications.scalars().all()


@router.put("/{notification_id}")
async def mark_notification_as_read(
    notification_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    notification = await db.execute(
        select(Notification).where(Notification.id == notification_id)
    )
    notification = notification.scalar_one_or_none()
    if not notification:
        logger.warning(f"Notification with ID '{notification_id}' not found.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found"
        )
    notification.mark_as_read()
    await db.commit()
    logger.info(
        f"Notification '{notification_id}' marked as read by user '{current_user.email}'."
    )
    return {"message": "Notification marked as read"}


# Add other notification endpoints (DELETE /notifications/{notification_id}, etc.)
