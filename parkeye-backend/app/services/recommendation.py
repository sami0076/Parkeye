"""Recommendation service - rank lots by predicted occupancy + walk distance."""
import math
from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Lot, OccupancySnapshot, CampusEvent
from app.services.prediction import get_prediction_at_hour


# Johnson Center (main campus) - default destination
JC_LAT = 38.8318
JC_LON = -77.3075

# Average walking speed: ~3 mph = 80 meters per minute
WALK_SPEED_M_PER_MIN = 80


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Haversine distance in km."""
    R = 6371  # Earth radius km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.asin(math.sqrt(a))
    return R * c


def walk_minutes(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Estimated walk time in minutes."""
    km = haversine_km(lat1, lon1, lat2, lon2)
    meters = km * 1000
    return meters / WALK_SPEED_M_PER_MIN


def pct_to_color(pct: float) -> str:
    if pct < 0.6:
        return "green"
    if pct < 0.85:
        return "yellow"
    return "red"


async def get_recommendations(
    session: AsyncSession,
    permit_type: str,
    dest_lat: float,
    dest_lon: float,
    arrival_time: datetime,
    duration_min: int = 60,
) -> list[dict]:
    """
    Filter lots by permit type, fetch predicted occupancy at arrival_hour,
    apply +20% event bump for affected lots, compute walk distance, sort by pct ASC.
    Returns top 5 lots with predicted_pct, color, walk_minutes, confidence.
    """
    # 1. Filter lots by permit type
    lots_result = await session.execute(
        select(Lot).where(Lot.permit_types.contains([permit_type]))
    )
    lots = lots_result.scalars().all()

    if not lots:
        return []

    from datetime import timedelta
    arrival_hour = arrival_time.hour
    arrival_dow = arrival_time.weekday()
    arrival_end = arrival_time + timedelta(minutes=duration_min)

    # 2. Get events overlapping arrival window
    events_result = await session.execute(
        select(CampusEvent).where(
            CampusEvent.start_time <= arrival_end,
            CampusEvent.end_time >= arrival_time,
        )
    )
    events = events_result.scalars().all()
    affected_lot_ids = set()
    for ev in events:
        affected_lot_ids.update(ev.affected_lots)

    # 3. For each lot: predicted occupancy + event bump
    candidates = []
    for lot in lots:
        pct, color = await get_prediction_at_hour(
            session, lot.id, arrival_hour, arrival_dow
        )
        if lot.id in affected_lot_ids:
            pct = min(1.0, pct + 0.20)
            color = pct_to_color(pct)

        walk_mins = walk_minutes(lot.lat, lot.lon, dest_lat, dest_lon)

        candidates.append({
            "lot_id": lot.id,
            "name": lot.name,
            "lat": lot.lat,
            "lon": lot.lon,
            "predicted_pct": pct,
            "color": color,
            "walk_minutes": round(walk_mins, 1),
        })

    # 4. Sort by occupancy_pct ASC (less full = better), then by walk_minutes
    candidates.sort(key=lambda x: (x["predicted_pct"], x["walk_minutes"]))

    # 5. Top 5
    top5 = candidates[:5]
    for c in top5:
        c["confidence"] = "Estimated from historical patterns"

    return top5
