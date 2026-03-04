"""Recommendation schemas."""
from uuid import UUID
from pydantic import BaseModel


class RecommendationLot(BaseModel):
    """Single lot recommendation."""

    lot_id: UUID
    name: str
    lat: float
    lon: float
    predicted_pct: float
    color: str
    walk_minutes: float
    confidence: str = "Estimated from historical patterns"


class RecommendationResponse(BaseModel):
    """Top 5 recommended lots."""

    recommendations: list[RecommendationLot]
