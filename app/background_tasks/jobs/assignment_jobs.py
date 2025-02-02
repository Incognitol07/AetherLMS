# app/background_tasks/jobs/assignment_jobs.py
from app.models import Assignment, Notification
from app.database import SessionLocal
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, update, delete

async def handle_assignment_reminders():
    async with SessionLocal() as db:
        result = await db.execute(
            select(Assignment).where(
                Assignment.due_date <= datetime.now(timezone.utc) + timedelta(hours=24),
                Assignment.due_date > datetime.now(timezone.utc)
            )
        )
        upcoming_assignments = result.scalars().all()
        
        for assignment in upcoming_assignments:
            for submission in assignment.submissions:
                if not submission.submitted_at:
                    notification = Notification(
                        user_id=submission.student.user.id,
                        message=f"Reminder: {assignment.title} due soon!",
                    )
                    db.add(notification)
        db.commit()

# TODO: make completely async 
async def close_expired_assignments():
    async with SessionLocal() as db:
        expired_assignments = db.query(Assignment).filter(
            Assignment.due_date < datetime.now(timezone.utc)
        ).all()

        for assignment in expired_assignments:
            assignment.status = 'closed'
            for submission in assignment.submissions:
                if not submission.submitted_at:
                    submission.status = 'late'
        db.commit()