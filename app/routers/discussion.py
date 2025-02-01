# app/routers/discussion.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import Discussion, Comment, User
from app.utils import (
    get_current_user, 
    logger
    )

router = APIRouter(prefix="/discussions", tags=["discussions"])


@router.post("/")
async def create_discussion(
    discussion_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        discussion = Discussion(**discussion_data, user_id=current_user.id)
        db.add(discussion)
        await db.commit()
        logger.info(f"Discussion created by user '{current_user.email}'.")
        return {"message": "Discussion created successfully"}
    except Exception as e:
        logger.error(f"Error creating discussion: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.post("/{discussion_id}/comments")
async def add_comment(
    discussion_id: str,
    comment_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        comment = Comment(
            **comment_data, discussion_id=discussion_id, user_id=current_user.id
        )
        db.add(comment)
        await db.commit()
        logger.info(
            f"Comment added to discussion '{discussion_id}' by user '{current_user.email}'."
        )
        return {"message": "Comment added successfully"}
    except Exception as e:
        logger.error(f"Error adding comment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


# Add other discussion endpoints (GET /discussions/{discussion_id}, PUT /discussions/{discussion_id}, etc.)
