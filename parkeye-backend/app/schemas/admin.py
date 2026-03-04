"""Admin schemas."""
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class AdminStatusUpdate(BaseModel):
    """Request body for PATCH /admin/lots/{id}/status."""

    status: str  # open | limited | closed
    status_until: datetime | None = None
    status_reason: str | None = None
