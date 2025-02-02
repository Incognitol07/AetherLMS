# app/background_tasks/jobs/submission_jobs.py
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from difflib import SequenceMatcher
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
from typing import List, Dict, Any
from app.models import (
    Submission,
    Assignment,
    Course,
    Notification,
    NotificationType,
    BackgroundTaskType,
)
import uuid
from app.database import AsyncSessionLocal
from ..decorators import with_task_tracking


# @with_task_tracking(BackgroundTaskType.PLAGIARISM)
async def check_submission_plagiarism(submission_id: uuid.UUID) -> Dict[str, Any]:
    """
    Enhanced plagiarism detection with:
    - Text normalization
    - Multiple similarity metrics
    - Match highlighting
    - Threshold-based alerts
    """
    async with AsyncSessionLocal() as db:
        # Get submission with full relationships
        submission_result = await db.execute(
            select(Submission)
            .options(
                selectinload(Submission.assignment)
                .selectinload(Assignment.submissions)
                .selectinload(Submission.student),
                selectinload(Submission.student),
            )
            .where(Submission.id == submission_id)
        )
        submission = submission_result.scalar_one()

        # Get all other submissions for this assignment
        other_submissions = [
            s
            for s in submission.assignment.submissions
            if s.id != submission_id and s.content
        ]

        # Preprocess content
        current_content = preprocess_content(submission.content)
        other_contents = [preprocess_content(s.content) for s in other_submissions]

        # Calculate similarities
        similarity_report = calculate_similarity_report(
            current_content, other_contents, other_submissions
        )

        # Update submission with results
        submission.plagiarism_score = similarity_report["max_score"]
        submission.plagiarism_report = similarity_report

        # Handle high similarity cases
        if submission.plagiarism_score > 0.75:
            await handle_plagiarism_alert(submission)

        await db.commit()
        return submission.plagiarism_report


def preprocess_content(content: str) -> str:
    """Normalize content for better comparison"""
    if not content:
        return ""

    # Remove code comments and special characters
    content = re.sub(r"#.*|\/\/.*|\/\*.*?\*\/", "", content, flags=re.DOTALL)
    # Normalize whitespace and lowercase
    return re.sub(r"\s+", " ", content).strip().lower()


def calculate_similarity_report(
    source_text: str, target_texts: List[str], submissions: List[Submission]
) -> Dict[str, Any]:
    """Calculate multiple similarity metrics and generate report"""
    if not target_texts:
        return {"max_score": 0.0, "similarities": [], "techniques_used": []}

    # TF-IDF Cosine Similarity
    vectorizer = TfidfVectorizer(ngram_range=(3, 5), analyzer="char_wb")
    tfidf_matrix = vectorizer.fit_transform([source_text] + target_texts)
    cosine_sims = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])[0]

    # Sequence Matcher
    sequence_sims = [
        SequenceMatcher(None, source_text, text).ratio() for text in target_texts
    ]

    # Combine results
    similarities = []
    for idx, sub in enumerate(submissions):
        similarities.append(
            {
                "submission_id": str(sub.id),
                "student_id": str(sub.student.id),
                "similarity_scores": {
                    "cosine": float(cosine_sims[idx]),
                    "sequence": float(sequence_sims[idx]),
                    "combined": max(cosine_sims[idx], sequence_sims[idx]),
                },
                "matched_sections": find_matching_blocks(
                    source_text, target_texts[idx]
                ),
            }
        )

    max_score = max(
        [s["similarity_scores"]["combined"] for s in similarities], default=0.0
    )

    return {
        "max_score": max_score,
        "similarities": similarities,
        "techniques_used": ["TF-IDF Cosine", "Sequence Matching"],
        "threshold": 0.75,
        "content_length": len(source_text),
    }


def find_matching_blocks(a: str, b: str, min_length: int = 50) -> List[Dict]:
    """Identify significant matching text sections"""
    matcher = SequenceMatcher(None, a, b)
    return [
        {
            "source_start": m.a,
            "source_end": m.a + m.size,
            "match_start": m.b,
            "match_end": m.b + m.size,
            "content": a[m.a : m.a + m.size],
        }
        for m in matcher.get_matching_blocks()
        if m.size > min_length
    ]


async def handle_plagiarism_alert(submission: Submission):
    """Create notifications for detected plagiarism"""
    async with AsyncSessionLocal() as db:
        # Notify instructors
        assignment_result = await db.execute(
            select(Assignment)
            .options(selectinload(Assignment.course).selectinload(Course.instructors))
            .where(Assignment.id == submission.assignment_id)
        )
        assignment = assignment_result.scalar_one()

        for instructor in assignment.course.instructors:
            notification = Notification(
                user_id=instructor.id,
                notification_type=NotificationType.PLAGIARISM,
                message=f"Potential plagiarism detected in submission for {assignment.title}",
                additional_data={
                    "submission_id": str(submission.id),
                    "student_id": str(submission.student.id),
                    "score": submission.plagiarism_score,
                    "assignment_id": str(assignment.id),
                },
            )
            db.add(notification)

        # Notify student
        student_notification = Notification(
            user_id=submission.student.user.id,
            notification_type=NotificationType.PLAGIARISM,
            message=f"Your submission for {assignment.title} requires review",
            additional_data={
                "submission_id": str(submission.id),
                "assignment_id": str(assignment.id),
                "score": submission.plagiarism_score,
            },
        )
        db.add(student_notification)


# @with_task_tracking(BackgroundTaskType.GRADE)
async def notify_instructors_for_grading(assignment_id: uuid.UUID):
    """Enhanced grading notification with submission context"""
    async with AsyncSessionLocal() as db:
        # Get assignment with ungraded submissions
        assignment_result = await db.execute(
            select(Assignment)
            .options(
                selectinload(Assignment.course).selectinload(Course.instructors),
                selectinload(Assignment.submissions),
            )
            .where(Assignment.id == assignment_id)
        )
        assignment = assignment_result.scalar_one()

        # Count ungraded submissions
        ungraded_count = sum(1 for s in assignment.submissions if s.grade is None)

        if ungraded_count > 0:
            for instructor in assignment.course.instructors:
                notification = Notification(
                    user_id=instructor.id,
                    notification_type=NotificationType.GRADE,
                    message=f"{ungraded_count} submissions need grading for {assignment.title}",
                    additional_data={
                        "assignment_id": str(assignment.id),
                        "course_id": str(assignment.course.id),
                        "ungraded_count": ungraded_count,
                        "due_date": (
                            assignment.due_date.isoformat()
                            if assignment.due_date
                            else None
                        ),
                    },
                )
                db.add(notification)

            await db.commit()
