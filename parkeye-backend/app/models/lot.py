"""Lot model - parking lot definitions."""
import uuid
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID, ARRAY as PG_ARRAY

from app.database import Base


class Lot(Base):
    """Parking lot table."""

    __tablename__ = "lots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)
    capacity = Column(Integer, nullable=False)
    permit_types = Column(PG_ARRAY(Text), nullable=False, default=list)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    is_deck = Column(Boolean, default=False)
    floors = Column(Integer, nullable=True)
    status = Column(String(20), default="open")  # open | limited | closed
    status_until = Column(DateTime(timezone=True), nullable=True)
    status_reason = Column(Text, nullable=True)
