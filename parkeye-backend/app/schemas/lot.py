"""Lot schemas."""
from uuid import UUID
from pydantic import BaseModel, Field


class LotResponse(BaseModel):
    """Single lot with current occupancy and status."""

    id: UUID
    name: str
    capacity: int
    permit_types: list[str]
    lat: float
    lon: float
    is_deck: bool
    floors: int | None
    status: str
    status_reason: str | None
    occupancy_pct: float
    color: str


class LotDetailResponse(LotResponse):
    """Single lot with upcoming events affecting it."""

    upcoming_events: list[dict] = Field(default_factory=list)


class LotListResponse(BaseModel):
    """List of lots."""

    lots: list[LotResponse]


class LotHistoryPoint(BaseModel):
    """Single point in occupancy history."""

    hour_of_day: int
    day_of_week: int
    occupancy_pct: float
    color: str


class LotHistoryResponse(BaseModel):
    """Hourly occupancy for past 7 days."""

    lot_id: UUID
    history: list[dict]


class FloorOccupancy(BaseModel):
    """Per-floor occupancy for parking decks."""

    floor: int
    occupancy_pct: float
    color: str


class LotFloorsResponse(BaseModel):
    """Per-floor occupancy breakdown."""

    lot_id: UUID
    floors: list[FloorOccupancy]
