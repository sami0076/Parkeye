"""Recommendations router - GET /recommendations."""
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.recommendations import RecommendationResponse, RecommendationLot
from app.services.recommendation import get_recommendations

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("", response_model=RecommendationResponse)
async def get_recommendations_endpoint(
    permit_type: str | None = Query(None, description="e.g. general, west_campus. Omit or None for any permit type."),
    dest_lat: float = Query(..., description="Destination latitude"),
    dest_lon: float = Query(..., description="Destination longitude"),
    arrival_time: str = Query(..., description="ISO 8601 datetime"),
    duration_min: int = Query(60, description="Parking duration in minutes"),
    session: AsyncSession = Depends(get_db),
):
    """Top 5 recommended lots by predicted occupancy + walk distance."""
    try:
        arrival_dt = datetime.fromisoformat(arrival_time.replace("Z", "+00:00"))
    except ValueError:
        arrival_dt = datetime.fromisoformat(arrival_time)

    recs = await get_recommendations(
        session,
        permit_type=permit_type,
        dest_lat=dest_lat,
        dest_lon=dest_lon,
        arrival_time=arrival_dt,
        duration_min=duration_min,
    )

    return RecommendationResponse(
        recommendations=[
            RecommendationLot(
                lot_id=r["lot_id"],
                name=r["name"],
                lat=r["lat"],
                lon=r["lon"],
                predicted_pct=r["predicted_pct"],
                color=r["color"],
                walk_minutes=r["walk_minutes"],
                confidence=r["confidence"],
            )
            for r in recs
        ]
    )
