# app/background_tasks/jobs/assignment_jobs.py
from app.models import (
    Assignment,
    Notification,
    BackgroundTaskType,
    NotificationType,
    Submission,
)
from ..decorators import with_task_tracking
from app.database import AsyncSessionLocal
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
import uuid


@with_task_tracking(BackgroundTaskType.ASSIGNMENT)
async def handle_assignment_reminders(task_id: uuid.UUID = None):
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Assignment)
            .where(
                Assignment.due_date <= datetime.now(timezone.utc) + timedelta(hours=24)
            )
            .options(
                selectinload(Assignment.submissions).selectinload(Submission.student)
            )
        )

        for assignment in result.scalars():
            for submission in assignment.submissions:
                if not submission.submitted_at:
                    notification = Notification(
                        user_id=submission.student.user.id,
                        message=f"Reminder: {assignment.title} due soon!",
                        notification_type=NotificationType.ASSIGNMENT,
                    )
                    db.add(notification)
        await db.commit()


@with_task_tracking(BackgroundTaskType.ASSIGNMENT)
async def close_expired_assignments(task_id: uuid.UUID = None):
    async with AsyncSessionLocal() as db:
        await db.execute(
            update(Assignment)
            .where(Assignment.due_date < datetime.now(timezone.utc))
            .values(status="closed")
        )

        result = await db.execute(
            select(Submission)
            .where(Submission.submitted_at.is_(None))
            .options(selectinload(Submission.assignment))
        )

        for submission in result.scalars():
            submission.status = "late"
            notification = Notification(
                user_id=submission.student.user.id,
                message=f"Late submission for {submission.assignment.title}",
                notification_type=NotificationType.DEADLINE,
            )
            db.add(notification)

        await db.commit()
