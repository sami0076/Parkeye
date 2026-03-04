"""Event schemas."""
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class EventResponse(BaseModel):
    """Campus event."""

    id: UUID
    title: str
    start_time: datetime
    end_time: datetime
    impact_level: str
    affected_lots: list[UUID]


class EventListResponse(BaseModel):
    """List of upcoming events."""

    events: list[EventResponse]
