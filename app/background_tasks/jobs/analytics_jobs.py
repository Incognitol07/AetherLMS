# app/background_tasks/jobs/analytics_jobs.py
from app.models import Course, Analytics, BackgroundTask
from app.database import SessionLocal

def generate_course_analytics(course_id):
    db = SessionLocal()
    try:
        course = db.query(Course).get(course_id)
        analytics = Analytics(course_id=course_id)
        
        # Calculate metrics
        analytics.enrollment_count = len(course.enrollments)
        analytics.average_grade = calculate_average_grade(course)
        analytics.completion_rate = calculate_completion_rate(course)
        
        db.add(analytics)
        db.commit()
    finally:
        db.close()

def update_all_student_progress():
    db = SessionLocal()
    try:
        students = db.query(Student).all()
        for student in students:
            progress = calculate_progress(student)
            student.progress = progress
        db.commit()
    finally:
        db.close()