"""Admin router - PATCH /admin/lots/{id}/status."""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Lot
from app.schemas.admin import AdminStatusUpdate
from app.auth import require_admin

router = APIRouter(prefix="/admin", tags=["admin"])


@router.patch("/lots/{lot_id}/status")
async def update_lot_status(
    lot_id: UUID,
    body: AdminStatusUpdate,
    session: AsyncSession = Depends(get_db),
    admin: object = Depends(require_admin),
):
    """Update lot status (open | limited | closed). Requires admin JWT."""
    result = await session.execute(select(Lot).where(Lot.id == lot_id))
    lot = result.scalars().first()
    if not lot:
        raise HTTPException(status_code=404, detail="Lot not found")

    lot.status = body.status
    lot.status_until = body.status_until
    lot.status_reason = body.status_reason

    return {"message": "Status updated", "lot_id": str(lot_id)}
