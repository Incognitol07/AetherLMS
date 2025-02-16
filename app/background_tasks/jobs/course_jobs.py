# app/background_tasks/jobs/course_jobs.py
from sqlalchemy import select, update, delete, and_
from sqlalchemy.orm import selectinload
from app.database import AsyncSessionLocal
from datetime import datetime, timedelta, timezone
import uuid
from ..decorators import with_task_tracking

from app.models import (
    Course,
    User,
    Student,
    Instructor,
    Enrollment,
    Module,
    Payment,
    Notification,
    NotificationType,
    BackgroundTaskType
)


@with_task_tracking(BackgroundTaskType.ENROLLMENT)
async def bulk_enroll_students(
    course_id: uuid.UUID, user_emails: list[str], task_id: uuid.UUID = None
):
    """
    Enroll multiple students in a course after verifying eligibility
    Handles duplicate enrollments gracefully
    """
    async with AsyncSessionLocal() as db:
        # Get the course with existing enrollments
        course_result = await db.execute(
            select(Course)
            .options(selectinload(Course.payments))
            .where(Course.id == course_id)
        )
        course = course_result.scalar_one()

        # Get existing enrolled student emails
        existing_enrollments = {
            enrollment.student.user.email for enrollment in course.enrollments
        }

        # Process new enrollments
        new_enrollments = []
        for email in user_emails:
            if email in existing_enrollments:
                continue

            # Find user and verify student status
            user_result = await db.execute(
                select(User)
                .where(User.email == email)
                .options(selectinload(User.students))
            )
            user = user_result.scalar()

            if user and user.students:
                # Check for successful payment
                payment_exists = any(
                    p.user_id == user.id and p.payment_status == "completed"
                    for p in course.payments
                )

                if payment_exists or course.is_free:
                    enrollment = Enrollment(
                        course_id=course_id, student_id=user.students.id
                    )
                    new_enrollments.append(enrollment)

                    # Send enrollment notification
                    notification = Notification(
                        user_id=user.id,
                        message=f"You've been enrolled in {course.title}",
                        notification_type=NotificationType.ENROLLMENT,
                    )
                    db.add(notification)

        db.add_all(new_enrollments)
        await db.commit()

        # Update course analytics
        await update_course_enrollment_stats(course_id)


@with_task_tracking(BackgroundTaskType.COURSE_DATA)
async def archive_completed_courses():
    """Archive courses that ended over 30 days ago and their related content"""
    async with AsyncSessionLocal() as db:
        # Find courses to archive
        result = await db.execute(
            select(Course)
            .where(
                and_(
                    Course.end_date < datetime.now(timezone.utc) - timedelta(days=30),
                    Course.status == "completed",
                )
            )
            .options(selectinload(Course.modules))
        )

        for course in result.scalars():
            course.status = "archived"

            # Archive modules
            await db.execute(
                update(Module)
                .where(Module.course_id == course.id)
                .values(status="archived")
            )

            # Notify instructors
            for instructor in course.instructors:
                notification = Notification(
                    user_id=instructor.id,
                    message=f"Course archived: {course.title}",
                    notification_type=NotificationType.COURSE_UPDATE,
                )
                db.add(notification)

        await db.commit()


@with_task_tracking(BackgroundTaskType.COURSE_DATA)
async def manage_course_instructors(
    course_id: uuid.UUID,
    instructor_ids: list[uuid.UUID],
    action: str,  # 'add' or 'remove'
):
    """Bulk add or remove instructors from a course with validation"""
    async with AsyncSessionLocal() as db:
        # Get course with existing instructors
        course_result = await db.execute(
            select(Course)
            .options(selectinload(Course.instructors))
            .where(Course.id == course_id)
        )
        course = course_result.scalar_one()

        # Get target instructors
        instructors_result = await db.execute(
            select(Instructor).where(Instructor.id.in_(instructor_ids))
        )
        target_instructors = instructors_result.scalars().all()

        if action == "add":
            for instructor in target_instructors:
                if instructor not in course.instructors:
                    course.instructors.append(instructor)
                    # Send notification
                    notification = Notification(
                        user_id=instructor.id,
                        message=f"Added as instructor to {course.title}",
                        notification_type=NotificationType.INSTRUCTOR,
                    )
                    db.add(notification)

        elif action == "remove":
            for instructor in target_instructors:
                if instructor in course.instructors:
                    course.instructors.remove(instructor)
                    # Send notification
                    notification = Notification(
                        user_id=instructor.id,
                        message=f"Removed from {course.title} instructors",
                        notification_type=NotificationType.INSTRUCTOR,
                    )
                    db.add(notification)

        await db.commit()
        await update_course_instructor_stats(course_id)


@with_task_tracking(BackgroundTaskType.COURSE_DATA)
async def process_course_expirations():
    """Notify users about upcoming course expirations"""
    async with AsyncSessionLocal() as db:
        # Find courses ending in 7 days
        result = await db.execute(
            select(Course)
            .where(
                and_(
                    Course.end_date.between(
                        datetime.now(timezone.utc) + timedelta(days=6),
                        datetime.now(timezone.utc) + timedelta(days=7),
                    ),
                    Course.status == "active",
                )
            )
            .options(
                selectinload(Course.enrollments)
                .selectinload(Enrollment.student)
                .selectinload(Student.user)
            )
        )

        for course in result.scalars():
            # Notify students
            for enrollment in course.enrollments:
                notification = Notification(
                    user_id=enrollment.student.user.id,
                    message=f"Course ending soon: {course.title}",
                    notification_type=NotificationType.DEADLINE,
                )
                db.add(notification)

            # Notify instructors
            for instructor in course.instructors:
                notification = Notification(
                    user_id=instructor.id,
                    message=f"Course ending soon: {course.title}",
                    notification_type=NotificationType.DEADLINE,
                )
                db.add(notification)

        await db.commit()


@with_task_tracking(BackgroundTaskType.DATA_CLEANUP)
async def reconcile_payments():
    """Clean up unpaid enrollments after 7 days"""
    async with AsyncSessionLocal() as db:
        # Find pending payments older than 7 days
        result = await db.execute(
            select(Payment)
            .where(
                and_(
                    Payment.payment_status == "pending",
                    Payment.created_at < datetime.now(timezone.utc) - timedelta(days=7),
                )
            )
            .options(selectinload(Payment.course), selectinload(Payment.user))
        )

        for payment in result.scalars():
            # Remove enrollment if exists
            await db.execute(
                delete(Enrollment).where(
                    and_(
                        Enrollment.course_id == payment.course_id,
                        Enrollment.student_id == payment.user.student.id,
                    )
                )
            )

            # Update payment status
            payment.payment_status = "failed"

            # Notify user
            notification = Notification(
                user_id=payment.user.id,
                message=f"Payment failed for {payment.course.title}",
                notification_type=NotificationType.PAYMENT,
            )
            db.add(notification)

        await db.commit()


async def update_course_enrollment_stats(course_id: uuid.UUID):
    """Update course enrollment metrics"""
    async with AsyncSessionLocal() as db:
        # Get enrollment count
        enrollments_count = await db.scalar(
            select(Enrollment).where(Enrollment.course_id == course_id).count()
        )

        # Update course statistics
        await db.execute(
            update(Course)
            .where(Course.id == course_id)
            .values(enrollment_count=enrollments_count)
        )

        await db.commit()


async def update_course_instructor_stats(course_id: uuid.UUID):
    """Update course instructor count"""
    async with AsyncSessionLocal() as db:
        instructor_count = await db.scalar(
            select(Course.instructors).where(Course.id == course_id).count()
        )

        await db.execute(
            update(Course)
            .where(Course.id == course_id)
            .values(instructor_count=instructor_count)
        )

        await db.commit()


@with_task_tracking(BackgroundTaskType.COURSE_DATA)
async def publish_scheduled_modules():
    """Activate modules based on their scheduled publish dates"""
    async with AsyncSessionLocal() as db:
        # Assuming Module has publish_date and status fields
        result = await db.execute(
            select(Module).where(
                and_(
                    Module.publish_date <= datetime.now(), Module.status == "scheduled"
                )
            )
        )

        for module in result.scalars():
            module.status = "active"
            # Notify course participants
            await notify_module_publication(module.id)

        await db.commit()


async def notify_module_publication(module_id: uuid.UUID):
    """Notify students when a new module is published"""
    async with AsyncSessionLocal() as db:
        # Get module with course and enrollments
        module_result = await db.execute(
            select(Module)
            .options(
                selectinload(Module.course)
                .selectinload(Course.enrollments)
                .selectinload(Enrollment.student)
                .selectinload(Student.user)
            )
            .where(Module.id == module_id)
        )
        module = module_result.scalar_one()

        for enrollment in module.course.enrollments:
            notification = Notification(
                user_id=enrollment.student.user.id,
                message=f"New module published: {module.title}",
                notification_type=NotificationType.COURSE_UPDATE,
            )
            db.add(notification)

        await db.commit()
