"""Test Open-Meteo forecast for all 6 Pune zones. Uses only stdlib."""
import csv
import json
import urllib.parse
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
ZONES_CSV = BASE / "backend" / "data" / "zones.csv"

VARS = "temperature_2m,relative_humidity_2m,wind_speed_10m,shortwave_radiation"

def check_zone(zone_id, lat, lon):
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": VARS,
        "forecast_days": 2,
        "timezone": "Asia/Kolkata",
    }
    url = "https://api.open-meteo.com/v1/forecast?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=30) as r:
        data = json.loads(r.read().decode())
    hourly = data.get("hourly", {})
    counts = {k: len(hourly.get(k, [])) for k in
              ["temperature_2m", "relative_humidity_2m", "wind_speed_10m", "shortwave_radiation"]}
    ok = all(v > 0 for v in counts.values())
    print(f"{zone_id}: lat={lat} lon={lon} -> {counts} {'OK' if ok else 'FAIL'}")
    return ok

def main():
    rows = list(csv.DictReader(ZONES_CSV.open()))
    print(f"Zones: {len(rows)}")
    results = [check_zone(r["zone_id"], r["lat"], r["lon"]) for r in rows]
    if all(results) and len(rows) == 6:
        print("PASS: 6 zones x 4 variables non-empty")
    else:
        print("FAIL: some zones missing data")
        raise SystemExit(1)

if __name__ == "__main__":
    main()
