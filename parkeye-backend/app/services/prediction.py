"""Prediction service - rule-based look-ahead (no ML)."""
from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import OccupancySnapshot


def pct_to_color(pct: float) -> str:
    """Convert occupancy pct to color."""
    if pct < 0.6:
        return "green"
    if pct < 0.85:
        return "yellow"
    return "red"


async def get_prediction(session: AsyncSession, lot_id: UUID) -> dict | None:
    """
    Rule-based look-ahead: fetch occupancy_snapshots for hour+1 and hour+2
    on the same day_of_week. Returns { t15: {pct, color}, t30: {pct, color}, note }.
    """
    now = datetime.utcnow()
    hour_of_day = now.hour
    day_of_week = now.weekday()

    hour_t15 = (hour_of_day + 1) % 24
    hour_t30 = (hour_of_day + 2) % 24

    result = await session.execute(
        select(OccupancySnapshot)
        .where(
            OccupancySnapshot.lot_id == lot_id,
            OccupancySnapshot.day_of_week == day_of_week,
            OccupancySnapshot.hour_of_day.in_([hour_t15, hour_t30]),
        )
    )
    snapshots = {s.hour_of_day: s for s in result.scalars().all()}

    t15_snap = snapshots.get(hour_t15)
    t30_snap = snapshots.get(hour_t30)

    if not t15_snap and not t30_snap:
        return None

    def to_slot(snap) -> dict:
        if snap:
            return {"pct": snap.occupancy_pct, "color": snap.color}
        return {"pct": 0.5, "color": "yellow"}

    return {
        "t15": to_slot(t15_snap),
        "t30": to_slot(t30_snap),
        "note": "Estimated from historical patterns",
    }


async def get_prediction_at_hour(
    session: AsyncSession, lot_id: UUID, hour_of_day: int, day_of_week: int
) -> tuple[float, str]:
    """
    Get predicted occupancy for a specific hour/day. Used by recommendations.
    Returns (occupancy_pct, color).
    """
    result = await session.execute(
        select(OccupancySnapshot)
        .where(
            OccupancySnapshot.lot_id == lot_id,
            OccupancySnapshot.hour_of_day == hour_of_day,
            OccupancySnapshot.day_of_week == day_of_week,
        )
    )
    snap = result.scalars().first()
    if snap:
        return (snap.occupancy_pct, snap.color)
    return (0.5, "yellow")
