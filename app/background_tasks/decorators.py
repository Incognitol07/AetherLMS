# app/background_tasks/decorators.py

from app.models import BackgroundTask, BackgroundTaskType
from app.database import AsyncSessionLocal
from sqlalchemy import update
import uuid
from functools import wraps
from celery import shared_task
from asgiref.sync import async_to_sync  



async def create_task_record(task_type: BackgroundTaskType, parameters: dict = None):
    async with AsyncSessionLocal() as db:
        task = BackgroundTask(
            task_type=task_type, 
            parameters=parameters, 
            status="pending"
        )
        db.add(task)
        await db.commit()
        await db.refresh(task)
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
        @shared_task(bind=True)
        @wraps(func)
        def sync_wrapper(self, *args, **kwargs):  # Change to sync wrapper
            # Wrap all async calls with async_to_sync
            task_id = async_to_sync(create_task_record)(task_type, kwargs)
            try:
                async_to_sync(update_task_status)(task_id, "processing")
                # Execute the original async func via async_to_sync
                result = async_to_sync(func)(*args, **kwargs, task_id=task_id)
                async_to_sync(update_task_status)(task_id, "completed", str(result))
                return result
            except Exception as e:
                async_to_sync(update_task_status)(task_id, "failed", str(e))
                raise self.retry(exc=e)
        return sync_wrapper
    return decorator