# app/routers/analytics.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models import Analytics, User
from app.utils import (
    get_current_student, 
    get_current_instructor, 
    logger
    )

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/")
async def get_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_student),
):
    analytics = await db.execute(
        select(Analytics).where(Analytics.student_id == current_user.id)
    )
    return analytics.scalars().all()


@router.get("/{student_id}")
async def get_student_analytics(
    student_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_instructor),
):
    analytics = await db.execute(
        select(Analytics).where(Analytics.student_id == student_id)
    )
    return analytics.scalars().all()


# Add other analytics endpoints (PUT /analytics/{student_id}, etc.)
