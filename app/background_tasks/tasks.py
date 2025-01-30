# app/background_tasks/tasks.py

from app.celery import celery_app
from app.models.assignment import Assignment
from app.models.notification import Notification
from app.models.submission import Submission
from app.database import SessionLocal
from datetime import datetime, timedelta

@celery_app.task(bind=True)
def send_assignment_reminders(self):
    try:
        db = SessionLocal()

        # Get assignments due within the next 24 hours
        upcoming_assignments = db.query(Assignment).filter(
            Assignment.due_date <= datetime.now() + timedelta(days=1),
            Assignment.due_date > datetime.now()
        ).all()

        # For each upcoming assignment, notify the corresponding students
        for assignment in upcoming_assignments:
            # Find all submissions for this assignment
            submissions_for_assignment = db.query(Submission).filter(
                Submission.assignment_id == assignment.id
            ).all()

            # For each submission, send a reminder to the student
            for submission in submissions_for_assignment:
                student = submission.student  # Each submission is linked to a student
                user = student.user  # The student has a relationship with the User model

                # Create and send the notification
                notification = Notification(
                    user_id=user.id,
                    message=f"Reminder: Your assignment '{assignment.title}' for course '{assignment.course.title}' is due soon!"
                )
                db.add(notification)

        db.commit()
        db.close()
    except Exception as e:
        db.rollback()  # Ensure to rollback the session in case of failure
        raise self.retry(exc=e)
