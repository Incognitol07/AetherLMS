# app/background_tasks/jobs/notification_jobs.py
from app.models import Notification, User, BackgroundTask, Assignment
from app.database import SessionLocal
from datetime import datetime, timedelta

def generate_daily_digest():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        for user in users:
            digest_content = build_digest_content(user)
            notification = Notification(
                user_id=user.id,
                message=digest_content,
                is_digest=True
            )
            db.add(notification)
        db.commit()
    finally:
        db.close()

def send_grade_notifications(assignment_id):
    db = SessionLocal()
    try:
        assignment = db.query(Assignment).get(assignment_id)
        for submission in assignment.submissions:
            if submission.grade:
                notification = Notification(
                    user_id=submission.student.user.id,
                    message=f"Grade posted for {assignment.title}: {submission.grade}%"
                )
                db.add(notification)
        db.commit()
    finally:
        db.close()