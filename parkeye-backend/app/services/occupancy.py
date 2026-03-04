"""Occupancy service - fetch current occupancy from snapshot table."""
from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Lot, OccupancySnapshot


def pct_to_color(pct: float) -> str:
    """Convert occupancy pct to color."""
    if pct < 0.6:
        return "green"
    if pct < 0.85:
        return "yellow"
    return "red"


async def get_current_occupancy(session: AsyncSession, lot_id: UUID) -> tuple[float, str] | None:
    """
    Get current occupancy for a lot from occupancy_snapshots.
    Returns (occupancy_pct, color) or None if not found.
    Admin override: if lot status is 'closed', returns (1.0, 'red').
    """
    now = datetime.utcnow()
    hour_of_day = now.hour
    day_of_week = now.weekday()  # 0=Monday, 6=Sunday

    # Check admin override
    lot_result = await session.execute(select(Lot).where(Lot.id == lot_id))
    lot = lot_result.scalars().first()
    if lot and lot.status == "closed":
        if lot.status_until and now > lot.status_until:
            pass  # Override expired, use snapshot
        else:
            return (1.0, "red")

    result = await session.execute(
        select(OccupancySnapshot)
        .where(
            OccupancySnapshot.lot_id == lot_id,
            OccupancySnapshot.hour_of_day == hour_of_day,
            OccupancySnapshot.day_of_week == day_of_week,
        )
    )
    snapshot = result.scalars().first()
    if snapshot:
        return (snapshot.occupancy_pct, snapshot.color)
    return None


async def get_all_current_occupancy(session: AsyncSession) -> list[dict]:
    """
    Get current occupancy for all lots. Used by WebSocket broadcast.
    Returns list of {lot_id, occupancy_pct, color}.
    """
    now = datetime.utcnow()
    hour_of_day = now.hour
    day_of_week = now.weekday()

    # Get all lots with their status
    lots_result = await session.execute(select(Lot))
    lots = {lot.id: lot for lot in lots_result.scalars().all()}

    # Get all snapshots for current hour/day
    snapshots_result = await session.execute(
        select(OccupancySnapshot)
        .where(
            OccupancySnapshot.hour_of_day == hour_of_day,
            OccupancySnapshot.day_of_week == day_of_week,
        )
    )
    snapshots = snapshots_result.scalars().all()

    result = []
    for snap in snapshots:
        lot = lots.get(snap.lot_id)
        if lot and lot.status == "closed":
            if lot.status_until and now > lot.status_until:
                pct, color = snap.occupancy_pct, snap.color
            else:
                pct, color = 1.0, "red"
        else:
            pct, color = snap.occupancy_pct, snap.color

        result.append({
            "lot_id": str(snap.lot_id),
            "occupancy_pct": pct,
            "color": color,
        })

    return result
