# app/background_tasks/tasks.py

from celery import shared_task
from .jobs import (
    assignment_jobs,
    submission_jobs,
    course_jobs,
    notification_jobs,
    analytics_jobs,
    system_jobs
)


# TODO: actually, out tasks that exists not nonexistent tasks that have not been created
@shared_task
def assignment_reminder_task():
    assignment_jobs.handle_assignment_reminders()

@shared_task
def auto_grade_submissions_task(assignment_id):
    submission_jobs.auto_grade_assignment_submissions(assignment_id)

@shared_task
def process_plagiarism_check_task(submission_id):
    submission_jobs.check_submission_plagiarism(submission_id)

@shared_task
def bulk_enroll_students_task(course_id, user_emails):
    course_jobs.bulk_enroll_students(course_id, user_emails)

@shared_task
def send_daily_digest_task():
    notification_jobs.generate_daily_digest()

@shared_task
def generate_course_report_task(course_id):
    analytics_jobs.generate_course_analytics(course_id)

@shared_task
def clean_old_submissions_task():
    system_jobs.clean_old_submissions()

@shared_task
def update_progress_records_task():
    analytics_jobs.update_all_student_progress()