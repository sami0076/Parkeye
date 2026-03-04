"""CampusEvent model - campus events affecting parking."""
import uuid
from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID, ARRAY

from app.database import Base


class CampusEvent(Base):
    """Campus event table."""

    __tablename__ = "campus_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    impact_level = Column(String(20), default="medium")  # low | medium | high
    affected_lots = Column(ARRAY(UUID(as_uuid=True)), nullable=False, default=list)
