"""Fetch 2-day forecast for all 6 zones and store in SQLite cache. Stdlib only."""
import csv
import json
import urllib.parse
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
ZONES_CSV = BASE / "backend" / "data" / "zones.csv"
DB = BASE / "backend" / "data" / "cache.sqlite"

VARS = "temperature_2m,relative_humidity_2m,wind_speed_10m,shortwave_radiation"


def fetch(lat, lon):
    params = {"latitude": lat, "longitude": lon, "hourly": VARS,
              "forecast_days": 2, "timezone": "Asia/Kolkata"}
    url = "https://api.open-meteo.com/v1/forecast?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.loads(r.read().decode())["hourly"]


def main():
    import sqlite3
    import sys
    sys.path.insert(0, str(BASE / "backend" / "app"))
    import cache as store

    conn = store.connect(DB)
    total = 0
    for row in csv.DictReader(ZONES_CSV.open()):
        h = fetch(row["lat"], row["lon"])
        rows = [{"time": t, "temp_c": te, "rh_pct": rh, "wind_kmh": w, "solar_wm2": s}
                for t, te, rh, w, s in zip(h["time"], h["temperature_2m"],
                                           h["relative_humidity_2m"],
                                           h["wind_speed_10m"],
                                           h["shortwave_radiation"])]
        n = store.save_hourly(conn, row["zone_id"], rows)
        total += n
        print(f'{row["zone_id"]}: saved {n} hours')
    print("counts:", store.zone_counts(conn))
    print(f"PASS: cached {total} rows in {DB.name}")


if __name__ == "__main__":
    main()
