"""Events router - GET /events."""
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import CampusEvent
from app.schemas.event import EventListResponse, EventResponse

router = APIRouter(prefix="/events", tags=["events"])


@router.get("", response_model=EventListResponse)
async def list_events(session: AsyncSession = Depends(get_db)):
    """Upcoming campus events for next 7 days."""
    now = datetime.utcnow()
    week_later = now + timedelta(days=7)

    result = await session.execute(
        select(CampusEvent)
        .where(
            CampusEvent.start_time >= now,
            CampusEvent.start_time <= week_later,
        )
        .order_by(CampusEvent.start_time)
    )
    events = result.scalars().all()

    return EventListResponse(
        events=[
            EventResponse(
                id=e.id,
                title=e.title,
                start_time=e.start_time,
                end_time=e.end_time,
                impact_level=e.impact_level or "medium",
                affected_lots=e.affected_lots or [],
            )
            for e in events
        ]
    )
