# app/routers/assignment.py

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import Assignment, Instructor, Student, Submission
from app.utils import (
    get_current_instructor, 
    get_current_student, 
    logger
    )

router = APIRouter(prefix="/assignments", tags=["assignments"])


@router.post("/")
async def create_assignment(
    assignment_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: Instructor = Depends(get_current_instructor),
):
    try:
        assignment = Assignment(**assignment_data)
        db.add(assignment)
        await db.commit()
        logger.info(
            f"Assignment '{assignment.title}' created by instructor '{current_user.email}'."
        )
        return {"message": "Assignment created successfully"}
    except Exception as e:
        logger.error(f"Error creating assignment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.post("/{assignment_id}/submissions")
async def submit_assignment(
    assignment_id: UUID,
    submission_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: Student = Depends(get_current_student),
):
    try:
        submission = Submission(
            **submission_data, assignment_id=assignment_id, student_id=current_user.id
        )
        db.add(submission)
        await db.commit()
        logger.info(
            f"Submission for assignment '{assignment_id}' created by student '{current_user.email}'."
        )
        return {"message": "Submission created successfully"}
    except Exception as e:
        logger.error(f"Error creating submission: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


# Add other assignment endpoints (GET /assignments/{assignment_id}, PUT /assignments/{assignment_id}, etc.)
