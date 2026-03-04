"""Lots router - GET /lots, /lots/{id}, /lots/{id}/history, /lots/{id}/floors."""
from datetime import datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Lot, OccupancySnapshot, CampusEvent
from app.schemas.lot import LotResponse, LotDetailResponse, LotHistoryResponse, LotFloorsResponse, FloorOccupancy
from app.services.occupancy import get_current_occupancy, pct_to_color

router = APIRouter(prefix="/lots", tags=["lots"])


@router.get("", response_model=list[LotResponse])
async def list_lots(session: AsyncSession = Depends(get_db)):
    """All lots with current occupancy_pct, color badge, and admin status."""
    result = await session.execute(select(Lot))
    lots = result.scalars().all()

    response = []
    for lot in lots:
        occ = await get_current_occupancy(session, lot.id)
        pct, color = (occ if occ else (0.5, "yellow"))

        response.append(LotResponse(
            id=lot.id,
            name=lot.name,
            capacity=lot.capacity,
            permit_types=lot.permit_types or [],
            lat=lot.lat,
            lon=lot.lon,
            is_deck=lot.is_deck or False,
            floors=lot.floors,
            status=lot.status or "open",
            status_reason=lot.status_reason,
            occupancy_pct=pct,
            color=color,
        ))
    return response


@router.get("/{lot_id}", response_model=LotDetailResponse)
async def get_lot(lot_id: UUID, session: AsyncSession = Depends(get_db)):
    """Single lot: occupancy, permit types, status, upcoming events affecting it."""
    result = await session.execute(select(Lot).where(Lot.id == lot_id))
    lot = result.scalars().first()
    if not lot:
        raise HTTPException(status_code=404, detail="Lot not found")

    occ = await get_current_occupancy(session, lot.id)
    pct, color = (occ if occ else (0.5, "yellow"))

    # Upcoming events affecting this lot (next 7 days)
    now = datetime.utcnow()
    week_later = now + timedelta(days=7)
    events_result = await session.execute(
        select(CampusEvent)
        .where(
            CampusEvent.start_time >= now,
            CampusEvent.start_time <= week_later,
        )
    )
    events = events_result.scalars().all()
    upcoming = [
        {"id": str(e.id), "title": e.title, "start_time": e.start_time.isoformat(), "end_time": e.end_time.isoformat()}
        for e in events
        if lot.id in (e.affected_lots or [])
    ]

    return LotDetailResponse(
        id=lot.id,
        name=lot.name,
        capacity=lot.capacity,
        permit_types=lot.permit_types or [],
        lat=lot.lat,
        lon=lot.lon,
        is_deck=lot.is_deck or False,
        floors=lot.floors,
        status=lot.status or "open",
        status_reason=lot.status_reason,
        occupancy_pct=pct,
        color=color,
        upcoming_events=upcoming,
    )


@router.get("/{lot_id}/history", response_model=LotHistoryResponse)
async def get_lot_history(lot_id: UUID, session: AsyncSession = Depends(get_db)):
    """Hourly occupancy for past 7 days (powers the detail screen graph)."""
    result = await session.execute(select(Lot).where(Lot.id == lot_id))
    if not result.scalars().first():
        raise HTTPException(status_code=404, detail="Lot not found")

    snapshots_result = await session.execute(
        select(OccupancySnapshot)
        .where(OccupancySnapshot.lot_id == lot_id)
        .order_by(OccupancySnapshot.day_of_week, OccupancySnapshot.hour_of_day)
    )
    snapshots = snapshots_result.scalars().all()

    history = [
        {
            "hour_of_day": s.hour_of_day,
            "day_of_week": s.day_of_week,
            "occupancy_pct": s.occupancy_pct,
            "color": s.color,
        }
        for s in snapshots
    ]

    return LotHistoryResponse(lot_id=lot_id, history=history)


@router.get("/{lot_id}/floors", response_model=LotFloorsResponse)
async def get_lot_floors(lot_id: UUID, session: AsyncSession = Depends(get_db)):
    """Per-floor occupancy breakdown for parking decks."""
    result = await session.execute(select(Lot).where(Lot.id == lot_id))
    lot = result.scalars().first()
    if not lot:
        raise HTTPException(status_code=404, detail="Lot not found")
    if not lot.is_deck or not lot.floors:
        raise HTTPException(status_code=400, detail="Lot is not a parking deck")

    occ = await get_current_occupancy(session, lot.id)
    base_pct, base_color = (occ if occ else (0.5, "yellow"))

    # For MVP: distribute occupancy across floors with slight variation
    floors = []
    for f in range(1, lot.floors + 1):
        # Slight variation: ground floor often fuller
        variation = 0.05 * (lot.floors - f) if f > 1 else 0.1
        pct = min(1.0, max(0, base_pct + variation))
        color = pct_to_color(pct)
        floors.append(FloorOccupancy(floor=f, occupancy_pct=pct, color=color))

    return LotFloorsResponse(lot_id=lot_id, floors=floors)
