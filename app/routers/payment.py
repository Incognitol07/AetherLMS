# app/routers/payment.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models import Payment, User
from app.utils import (
    get_current_user, 
    get_current_admin, 
    logger
    )

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/")
async def create_payment(
    payment_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        payment = Payment(**payment_data, user_id=current_user.id)
        db.add(payment)
        await db.commit()
        logger.info(f"Payment created by user '{current_user.email}'.")
        return {"message": "Payment created successfully"}
    except Exception as e:
        logger.error(f"Error creating payment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/")
async def list_payments(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_admin)
):
    payments = await db.execute(select(Payment))
    return payments.scalars().all()


# Add other payment endpoints (GET /payments/{payment_id}, PUT /payments/{payment_id}, etc.)
