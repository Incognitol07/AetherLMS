# app/background_tasks/jobs/assignment_jobs.py
from app.models import Assignment, Notification, BackgroundTask
from app.database import SessionLocal
from datetime import datetime, timedelta, timezone

def handle_assignment_reminders():
    db = SessionLocal()
    try:
        upcoming_assignments = db.query(Assignment).filter(
            Assignment.due_date <= datetime.now(timezone.utc) + timedelta(hours=24),
            Assignment.due_date > datetime.now(timezone.utc)
        ).all()

        for assignment in upcoming_assignments:
            for submission in assignment.submissions:
                if not submission.submitted_at:
                    notification = Notification(
                        user_id=submission.student.user.id,
                        message=f"Reminder: {assignment.title} due soon!",
                    )
                    db.add(notification)
        db.commit()
    finally:
        db.close()

def close_expired_assignments():
    db = SessionLocal()
    try:
        expired_assignments = db.query(Assignment).filter(
            Assignment.due_date < datetime.now(timezone.utc)
        ).all()

        for assignment in expired_assignments:
            assignment.status = 'closed'
            for submission in assignment.submissions:
                if not submission.submitted_at:
                    submission.status = 'late'
        db.commit()
    finally:
        db.close()