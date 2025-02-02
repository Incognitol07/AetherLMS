# app/background_tasks/jobs/submission_jobs.py
from app.models import Submission, Course, Assignment, Notification, NotificationType
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select
from app.database import SessionLocal
from difflib import SequenceMatcher
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

# TODO: improve plagiarism function, check better and add plagiarism attributes to submission model
async def check_submission_plagiarism(submission_id):
    async with SessionLocal() as db:
        # Get current submission
        submission = await db.get(Submission, submission_id)
        
        # Get previous submissions
        result = await db.execute(
            select(Submission.content)
            .where(Submission.assignment_id == submission.assignment_id)
            .where(Submission.id != submission_id)
        )
        previous_submissions = result.scalars().all()
        
        # Calculate similarity scores
        similarity_scores = []
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform([submission.content] + previous_submissions)
        cosine_similarities = np.dot(tfidf_matrix[0:1], tfidf_matrix[1:].T).toarray()
        
        submission.plagiarism_score = float(cosine_similarities.max())
        submission.plagiarism_report = {
            "similar_submissions": [
                {"id": sub.id, "similarity": score} 
                for sub, score in zip(previous_submissions, cosine_similarities[0])
            ]
        }
        
        await db.commit()

# jobs/submission_jobs.py
async def notify_instructors_for_grading(assignment_id):
    async with SessionLocal() as db:
        # Get assignment with instructor relations
        result = await db.execute(
            select(Assignment).options(selectinload(Assignment.course).selectinload(Course.instructors))
            .where(Assignment.id == assignment_id)
        )
        assignment = result.scalar()
        
        # Create grading tasks
        for instructor in assignment.course.instructors:
            notification = Notification(
                user_id=instructor.id,
                message=f"New submissions to grade for {assignment.title}",
                notification_type=NotificationType.INSTRUCTOR
            )
            db.add(notification)
        
        await db.commit()