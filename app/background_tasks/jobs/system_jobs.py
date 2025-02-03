# app/background_tasks/jobs/system_jobs.py
from app.models import Submission, BackgroundTask
from app.database import AsyncSessionLocal
from datetime import datetime, timedelta, timezone
from ..decorators import with_task_tracking
import uuid
from sqlalchemy.orm import selectinload
from app.models import Submission, Notification, BackgroundTaskType, NotificationType
from sqlalchemy import delete, select


@with_task_tracking(BackgroundTaskType.DATA_CLEANUP)
async def clean_old_submissions(days=365, task_id: uuid.UUID = None):
    async with AsyncSessionLocal() as db:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)

        # Get submissions to delete
        result = await db.execute(
            select(Submission)
            .where(Submission.submitted_at < cutoff)
            .options(selectinload(Submission.student))
        )

        deleted_count = 0
        for submission in result.scalars():
            notification = Notification(
                user_id=submission.student.user.id,
                message=f"Submission archived: {submission.assignment.title}",
                notification_type=NotificationType.SYSTEM,
            )
            db.add(notification)
            deleted_count += 1

        await db.execute(delete(Submission).where(Submission.submitted_at < cutoff))
        await db.commit()
    return f"Deleted {deleted_count} old submissions"


@with_task_tracking(BackgroundTaskType.DATA_BACKUP)
async def perform_database_backup():
    # Implementation for database backup
    pass


@with_task_tracking(BackgroundTaskType.DATA_CLEANUP)
async def clean_old_tasks(days=30):
    async with AsyncSessionLocal() as db:
        await db.execute(
            delete(BackgroundTask).where(
                BackgroundTask.created_at < datetime.now() - timedelta(days=days)
            )
        )
