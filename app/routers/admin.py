# app/routers/admin.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models import Role, Admin
from app.utils import (
    get_current_admin, 
    logger
    )

router = APIRouter(prefix="/admin", tags=["admin"])

@router.post("/roles")
async def create_role(role_data: dict, db: AsyncSession = Depends(get_db), current_user: Admin = Depends(get_current_admin)):
    try:
        role = Role(name=role_data["name"], permissions=role_data.get("permissions", []))
        db.add(role)
        await db.commit()
        logger.info(f"Role '{role.name}' created by admin '{current_user.email}'.")
        return {"message": "Role created successfully"}
    except Exception as e:
        logger.error(f"Error creating role: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.get("/roles")
async def list_roles(db: AsyncSession = Depends(get_db), current_user: Admin = Depends(get_current_admin)):
    roles = await db.execute(select(Role))
    return roles.scalars().all()

# Add other admin endpoints (GET /roles/{role_id}, PUT /roles/{role_id}, DELETE /roles/{role_id}, etc.)