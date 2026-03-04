"""Feedback router - POST /feedback."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Lot, Feedback
from app.schemas.feedback import FeedbackCreate, FeedbackResponse
from app.auth import get_current_user, User

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("", response_model=FeedbackResponse)
async def create_feedback(
    body: FeedbackCreate,
    session: AsyncSession = Depends(get_db),
    user: User | None = Depends(get_current_user),
):
    """Submit user feedback on lot accuracy."""
    result = await session.execute(select(Lot).where(Lot.id == body.lot_id))
    if not result.scalars().first():
        raise HTTPException(status_code=404, detail="Lot not found")

    feedback = Feedback(
        user_id=user.id if user else None,
        lot_id=body.lot_id,
        accuracy_rating=body.accuracy_rating,
        experience_rating=body.experience_rating,
        note=body.note,
    )
    session.add(feedback)
    await session.flush()

    return FeedbackResponse(
        id=feedback.id,
        lot_id=feedback.lot_id,
        message="Thank you for your feedback!",
    )
