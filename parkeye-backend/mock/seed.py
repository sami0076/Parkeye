"""Seed Supabase database with mock data. Idempotent - safe to re-run."""
import asyncio
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import engine, AsyncSessionLocal, Base
from app.models import Lot, OccupancySnapshot, CampusEvent

MOCK_DIR = Path(__file__).parent
LOTS_FILE = MOCK_DIR / "lots.json"
OCCUPANCY_FILE = MOCK_DIR / "occupancy_history.csv"
EVENTS_FILE = MOCK_DIR / "events.json"


async def create_tables():
    """Create all tables if they don't exist."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tables created.")


async def seed_lots(session: AsyncSession):
    """Seed lots. Skips existing by name."""
    with open(LOTS_FILE) as f:
        lots_data = json.load(f)

    added = 0
    for lot_data in lots_data:
        result = await session.execute(
            select(Lot).where(Lot.name == lot_data["name"])
        )
        if result.scalars().first():
            continue

        session.add(Lot(
            id=lot_data["id"],
            name=lot_data["name"],
            capacity=lot_data["capacity"],
            permit_types=lot_data["permit_types"],
            lat=lot_data["lat"],
            lon=lot_data["lon"],
            is_deck=lot_data.get("is_deck", False),
            floors=lot_data.get("floors"),
        ))
        added += 1

    await session.commit()
    print(f"Lots: {added} added, {len(lots_data) - added} already existed.")


async def seed_occupancy(session: AsyncSession):
    """Seed occupancy snapshots. Skip if already populated."""
    count_result = await session.execute(
        select(func.count()).select_from(OccupancySnapshot)
    )
    if count_result.scalar() > 0:
        print("Occupancy snapshots already seeded, skipping.")
        return

    with open(OCCUPANCY_FILE) as f:
        rows = list(csv.DictReader(f))

    batch_size = 200
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i + batch_size]
        for row in batch:
            session.add(OccupancySnapshot(
                lot_id=row["lot_id"],
                hour_of_day=int(row["hour_of_day"]),
                day_of_week=int(row["day_of_week"]),
                occupancy_pct=float(row["occupancy_pct"]),
                color=row["color"],
            ))
        await session.commit()
        print(f"  Occupancy: {min(i + batch_size, len(rows))}/{len(rows)}")

    print(f"Seeded {len(rows)} occupancy snapshots.")


async def seed_events(session: AsyncSession):
    """Seed campus events. Skips duplicates by title + start_time."""
    from datetime import datetime

    with open(EVENTS_FILE) as f:
        events_data = json.load(f)

    added = 0
    for ev in events_data:
        start = datetime.fromisoformat(ev["start_time"].replace("Z", "+00:00"))
        result = await session.execute(
            select(CampusEvent).where(
                CampusEvent.title == ev["title"],
                CampusEvent.start_time == start,
            )
        )
        if result.scalars().first():
            continue

        end = datetime.fromisoformat(ev["end_time"].replace("Z", "+00:00"))
        session.add(CampusEvent(
            title=ev["title"],
            start_time=start,
            end_time=end,
            impact_level=ev.get("impact_level", "medium"),
            affected_lots=ev["affected_lots"],
        ))
        added += 1

    await session.commit()
    print(f"Events: {added} added, {len(events_data) - added} already existed.")


async def main():
    from urllib.parse import urlparse
    host = urlparse(settings.DATABASE_URL).hostname
    print(f"Connecting to: {host}")

    print("Creating tables...")
    await create_tables()

    async with AsyncSessionLocal() as session:
        print("Seeding lots...")
        await seed_lots(session)

        print("Seeding occupancy...")
        await seed_occupancy(session)

        print("Seeding events...")
        await seed_events(session)

    print("\nSeed complete!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"\nSeed failed: {e}")
        print("\nCheck:")
        print("  1. DATABASE_URL in .env uses the Session pooler connection string")
        print("  2. Get it from: Supabase Dashboard -> Connect button -> Session pooler")
        print("  3. Replace postgresql:// with postgresql+asyncpg://")
        print("  4. Password is correct (no special chars unencoded)")
        from urllib.parse import urlparse
        try:
            host = urlparse(settings.DATABASE_URL).hostname
            print(f"  Current host: {host}")
        except Exception:
            pass
        sys.exit(1)
