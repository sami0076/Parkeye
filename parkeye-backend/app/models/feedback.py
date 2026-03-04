"""Feedback model - user feedback on lot accuracy."""
import uuid
from sqlalchemy import Column, Integer, Text, DateTime, func
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class Feedback(Base):
    """User feedback table."""

    __tablename__ = "feedback"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=True)  # From Supabase Auth JWT
    lot_id = Column(UUID(as_uuid=True), nullable=False)
    accuracy_rating = Column(Integer, nullable=False)  # 1-5
    experience_rating = Column(Integer, nullable=False)  # 1-5
    note = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
