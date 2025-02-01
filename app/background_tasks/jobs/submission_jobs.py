# app/background_tasks/jobs/submission_jobs.py
from app.models import Submission, BackgroundTask, Assignment
from app.database import SessionLocal
from .media_jobs import plagiarism_checker, auto_grader
from datetime import datetime, timezone

def check_submission_plagiarism(submission_id):
    db = SessionLocal()
    try:
        submission = db.query(Submission).get(submission_id)
        result = plagiarism_checker.analyze(submission.content)
        
        submission.plagiarism_score = result['score']
        submission.plagiarism_report = result['report']
        db.commit()
        
        if result['score'] > 0.8:
            # handle_plagiarism_alert(submission)
            return
    finally:
        db.close()

def auto_grade_assignment_submissions(assignment_id):
    db = SessionLocal()
    try:
        assignment = db.query(Assignment).get(assignment_id)
        for submission in assignment.submissions:
            if submission.submitted_at and not submission.grade:
                grade = auto_grader.grade(submission.content)
                submission.grade = grade
                submission.graded_at = datetime.now(timezone.utc)
        db.commit()
    finally:
        db.close()