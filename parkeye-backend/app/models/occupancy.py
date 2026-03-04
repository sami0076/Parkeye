"""OccupancySnapshot model - pre-populated hourly occupancy data."""
from sqlalchemy import Column, Integer, Float, String, BigInteger, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class OccupancySnapshot(Base):
    """Occupancy snapshot table - hour_of_day + day_of_week per lot."""

    __tablename__ = "occupancy_snapshots"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    lot_id = Column(UUID(as_uuid=True), ForeignKey("lots.id", ondelete="CASCADE"), nullable=False)
    hour_of_day = Column(Integer, nullable=False)  # 0-23
    day_of_week = Column(Integer, nullable=False)  # 0=Monday, 6=Sunday
    occupancy_pct = Column(Float, nullable=False)  # 0.0 to 1.0
    color = Column(String(20), nullable=False)  # green | yellow | red
