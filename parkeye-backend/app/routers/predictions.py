"""Predictions router - GET /predictions/{lot_id}."""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Lot
from app.schemas.occupancy import PredictionResponse, PredictionSlot
from app.services.prediction import get_prediction

router = APIRouter(prefix="/predictions", tags=["predictions"])


@router.get("/{lot_id}", response_model=PredictionResponse)
async def get_prediction_endpoint(lot_id: UUID, session: AsyncSession = Depends(get_db)):
    """Rule-based look-ahead: t15 and t30 predictions from historical patterns."""
    result = await session.execute(select(Lot).where(Lot.id == lot_id))
    if not result.scalars().first():
        raise HTTPException(status_code=404, detail="Lot not found")

    pred = await get_prediction(session, lot_id)
    if not pred:
        return PredictionResponse(
            t15=PredictionSlot(pct=0.5, color="yellow"),
            t30=PredictionSlot(pct=0.5, color="yellow"),
            note="Estimated from historical patterns",
        )

    return PredictionResponse(
        t15=PredictionSlot(pct=pred["t15"]["pct"], color=pred["t15"]["color"]),
        t30=PredictionSlot(pct=pred["t30"]["pct"], color=pred["t30"]["color"]),
        note=pred["note"],
    )
