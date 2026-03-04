"""Generate mock/occupancy_history.csv using the formula from CONTEXT.md."""
import csv
import math
import random
from pathlib import Path

LOT_IDS = [
    "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d",
    "b2c3d4e5-f6a7-5b6c-9d0e-1f2a3b4c5d6e",
    "c3d4e5f6-a7b8-6c7d-0e1f-2a3b4c5d6e7f",
    "d4e5f6a7-b8c9-7d8e-1f2a-3b4c5d6e7f8a",
    "e5f6a7b8-c9d0-8e9f-2a3b-4c5d6e7f8a9b",
    "f6a7b8c9-d0e1-9f0a-3b4c-5d6e7f8a9b0c",
    "a7b8c9d0-e1f2-0a1b-4c5d-6e7f8a9b0c1d",
    "b8c9d0e1-f2a3-1b2c-5d6e-7f8a9b0c1d2e",
    "c9d0e1f2-a3b4-2c3d-6e7f-8a9b0c1d2e3f",
    "d0e1f2a3-b4c5-3d4e-7f8a-9b0c1d2e3f4a",
]


def sin_curve(hour: int, peak: int = 10, trough: int = 3) -> float:
    """Sinusoidal curve peaking at 10 AM, trough at 3 AM."""
    # Map hour to a value: peak at 10, trough at 3
    # Use a bell-like curve
    center = peak
    spread = 4
    return max(0, 0.3 + 0.6 * math.exp(-((hour - center) ** 2) / (2 * spread**2)))


def pct_to_color(pct: float) -> str:
    """Convert occupancy pct to color."""
    if pct < 0.6:
        return "green"
    if pct < 0.85:
        return "yellow"
    return "red"


def main():
    random.seed(42)
    out_path = Path(__file__).parent / "occupancy_history.csv"

    with open(out_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["lot_id", "hour_of_day", "day_of_week", "occupancy_pct", "color"])

        for lot_id in LOT_IDS:
            for day_of_week in range(7):  # 0=Mon, 6=Sun
                weekend_factor = 0.4 if day_of_week >= 5 else 1.0
                for hour_of_day in range(24):
                    base = sin_curve(hour_of_day)
                    noise = random.gauss(0, 0.05)
                    pct = max(0.0, min(1.0, base * weekend_factor + noise))
                    color = pct_to_color(pct)
                    writer.writerow([lot_id, hour_of_day, day_of_week, round(pct, 4), color])

    print(f"Generated {out_path}")


if __name__ == "__main__":
    main()
