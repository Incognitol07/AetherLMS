# app/routers/background_task.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models import BackgroundTask, Admin
from app.utils import (
    get_current_admin, 
    logger
    )

router = APIRouter(prefix="/background-tasks", tags=["background-tasks"])


# @router.post("/")
# async def create_background_task(
#     task_data: dict,
#     db: AsyncSession = Depends(get_db),
#     current_user: Admin = Depends(get_current_admin),
# ):
#     try:
#         task = BackgroundTask(**task_data)
#         db.add(task)
#         await db.commit()
#         logger.info(f"Background task created by admin '{current_user.email}'.")
#         return {"message": "Background task created successfully"}
#     except Exception as e:
#         logger.error(f"Error creating background task: {e}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Internal server error",
#         )


# @router.get("/")
# async def list_background_tasks(
#     db: AsyncSession = Depends(get_db), current_user: Admin = Depends(get_current_admin)
# ):
#     tasks = await db.execute(select(BackgroundTask))
#     return tasks.scalars().all()


# Add other background task endpoints (GET /background-tasks/{task_id}, PUT /background-tasks/{task_id}, etc.)

# app/routers/background_tasks.py
# from app.background_tasks.tasks import database_backup_task

# router = APIRouter(prefix="/tasks", tags=["tasks"])

# @router.get("/trigger-backup")
# async def trigger_backup():
#     task = database_backup_task.delay()
#     return {"message": "Backup initiated", "task_id": task.id}