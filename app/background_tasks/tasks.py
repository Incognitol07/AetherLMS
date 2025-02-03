# app/background_tasks/tasks.py
from celery import shared_task
from .jobs import (
    assignment_jobs,
    submission_jobs,
    course_jobs,
    system_jobs,
)

@shared_task(bind=True)
async def assignment_reminder_task(self):
    await assignment_jobs.handle_assignment_reminders

@shared_task(bind=True)
async def close_expired_assignment_task(self):
    await assignment_jobs.close_expired_assignments


@shared_task(bind=True)
async def process_plagiarism_check_task(submission_id):
    await submission_jobs.check_submission_plagiarism(submission_id)

@shared_task(bind=True)
async def notify_instructors_for_grading_task(assignment_id):
    await submission_jobs.notify_instructors_for_grading(assignment_id)


@shared_task(bind=True)
async def clean_old_submissions_task(self):
    await system_jobs.clean_old_submissions

@shared_task(bind=True)
async def database_backup_task(self):
    await system_jobs.perform_database_backup

@shared_task(bind=True)
async def cleanup_tasks(self):
    await system_jobs.clean_old_tasks

@shared_task(bind=True)(bind=True)
async def bulk_enroll_students_task(self, course_id, user_emails):
    await course_jobs.bulk_enroll_students(course_id, user_emails)

@shared_task(bind=True)
async def archive_courses_task(self):
    await course_jobs.archive_completed_courses

@shared_task(bind=True)
async def manage_instructors_task(course_id, instructor_ids, action):
    await course_jobs.manage_course_instructors(course_id, instructor_ids, action)

@shared_task(bind=True)
async def process_course_expiration_task(self):
    await course_jobs.process_course_expirations

@shared_task(bind=True)
async def publish_modules_task(self):
    await course_jobs.publish_scheduled_modules