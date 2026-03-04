"""Feedback schemas."""
from uuid import UUID
from pydantic import BaseModel, Field


class FeedbackCreate(BaseModel):
    """Request body for submitting feedback."""

    lot_id: UUID
    accuracy_rating: int = Field(ge=1, le=5)
    experience_rating: int = Field(ge=1, le=5)
    note: str | None = None


class FeedbackResponse(BaseModel):
    """Feedback submission response."""

    id: UUID
    lot_id: UUID
    message: str = "Thank you for your feedback!"
