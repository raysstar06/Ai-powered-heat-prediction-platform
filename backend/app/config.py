"""Shared config: zones, thresholds, bands. Single source of truth."""
import csv
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
ZONES_CSV = BASE / "data" / "zones.csv"
COOLING_JSON = BASE / "data" / "cooling_centers.json"

BANDS = [(25, "Low"), (50, "Moderate"), (75, "High"), (101, "Extreme")]


def band_for(score: float) -> str:
    for limit, name in BANDS:
        if score < limit:
            return name
    return "Extreme"


def load_zones():
    with ZONES_CSV.open() as f:
        return list(csv.DictReader(f))
