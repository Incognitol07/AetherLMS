# app/background_tasks/jobs/analytics_jobs.py
from app.models import Course, Analytics, Student
from app.database import SessionLocal

# TODO: improve analytics model
# TODO: make async completely
# TODO: write helper functions
# async def generate_course_analytics(course_id):
#     async with SessionLocal() as db:
#         course = db.query(Course).get(course_id)
#         analytics = Analytics(course_id=course_id)
        
#         # Calculate metrics
#         analytics.enrollment_count = len(course.enrollments)
#         analytics.average_grade = calculate_average_grade(course)
#         analytics.completion_rate = calculate_completion_rate(course)
        
#         db.add(analytics)
#         db.commit()

# async def update_all_student_progress():
#     async with SessionLocal() as db:
#         students = db.query(Student).all()
#         for student in students:
#             progress = calculate_progress(student)
#             student.progress = progress
#         db.commit()