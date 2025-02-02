# app/background_tasks/tasks.py
from celery import shared_task
from .jobs import (
    assignment_jobs,
    submission_jobs,
    course_jobs,
    system_jobs,
)
from asgiref.sync import async_to_sync

@shared_task
def assignment_reminder_task():
    async_to_sync(assignment_jobs.handle_assignment_reminders)

@shared_task
def close_expired_assignment_task():
    async_to_sync(assignment_jobs.close_expired_assignments)


@shared_task
def process_plagiarism_check_task(submission_id):
    async_to_sync(submission_jobs.check_submission_plagiarism)(submission_id)

@shared_task
def notify_instructors_for_grading_task(assignment_id):
    async_to_sync(submission_jobs.notify_instructors_for_grading)(assignment_id)


@shared_task
def clean_old_submissions_task():
    async_to_sync(system_jobs.clean_old_submissions)

@shared_task
def database_backup_task():
    async_to_sync(system_jobs.perform_database_backup)

@shared_task
def cleanup_tasks():
    async_to_sync(system_jobs.clean_old_tasks)

@shared_task(bind=True, autoretry_for=(Exception,), max_retries=3)
def bulk_enroll_students_task(self, course_id, user_emails):
    try:
        async_to_sync(course_jobs.bulk_enroll_students)(course_id, user_emails)
    except Exception as e:
        self.retry(exc=e, countdown=2 ** self.request.retries)

@shared_task
def archive_courses_task():
    async_to_sync(course_jobs.archive_completed_courses)

@shared_task
def manage_instructors_task(course_id, instructor_ids, action):
    async_to_sync(course_jobs.manage_course_instructors)(course_id, instructor_ids, action)

@shared_task
def process_course_expiration_task():
    async_to_sync(course_jobs.process_course_expirations)

@shared_task
def publish_modules_task():
    async_to_sync(course_jobs.publish_scheduled_modules)