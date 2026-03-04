"""Occupancy and prediction schemas."""
from uuid import UUID
from pydantic import BaseModel


class OccupancyPoint(BaseModel):
    """Single occupancy data point."""

    lot_id: UUID
    occupancy_pct: float
    color: str


class OccupancyResponse(BaseModel):
    """Current occupancy for a lot."""

    lot_id: UUID
    occupancy_pct: float
    color: str


class PredictionSlot(BaseModel):
    """Prediction for a time slot."""

    pct: float
    color: str


class PredictionResponse(BaseModel):
    """Rule-based look-ahead prediction."""

    t15: PredictionSlot
    t30: PredictionSlot
    note: str = "Estimated from historical patterns"
