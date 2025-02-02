# app/background_tasks/decorators.py

from app.models import BackgroundTask, BackgroundTaskType
from app.database import AsyncSessionLocal
from sqlalchemy import update
import uuid



async def create_task_record(task_type: BackgroundTaskType, parameters: dict = None):
    async with AsyncSessionLocal() as db:
        task = BackgroundTask(
            task_type=task_type, parameters=parameters, status="pending"
        )
        db.add(task)
        await db.commit()
        return task.id


async def update_task_status(task_id: uuid.UUID, status: str, result: str = None):
    async with AsyncSessionLocal() as db:
        await db.execute(
            update(BackgroundTask)
            .where(BackgroundTask.id == task_id)
            .values(status=status, result=result)
        )
        await db.commit()


def with_task_tracking(task_type: BackgroundTaskType):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            task_id = await create_task_record(task_type, kwargs)
            try:
                await update_task_status(task_id, "processing")
                result = await func(*args, **kwargs, task_id=task_id)
                await update_task_status(task_id, "completed", str(result))
                return result
            except Exception as e:
                await update_task_status(task_id, "failed", str(e))
                raise
        return wrapper

    return decorator