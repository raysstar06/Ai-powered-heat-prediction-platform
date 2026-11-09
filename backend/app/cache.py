"""SQLite cache: stores hourly weather per zone. Stdlib only."""
import sqlite3
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
DEFAULT_DB = BASE / "data" / "cache.sqlite"

SCHEMA = """
CREATE TABLE IF NOT EXISTS hourly (
    zone_id TEXT NOT NULL,
    time TEXT NOT NULL,
    temp_c REAL, rh_pct REAL, wind_kmh REAL, solar_wm2 REAL,
    PRIMARY KEY (zone_id, time)
);
"""


def connect(path: str | Path = DEFAULT_DB) -> sqlite3.Connection:
    conn = sqlite3.connect(str(path))
    conn.execute(SCHEMA)
    conn.commit()
    return conn


def save_hourly(conn: sqlite3.Connection, zone_id: str, rows: list) -> int:
    conn.executemany(
        "INSERT OR REPLACE INTO hourly (zone_id,time,temp_c,rh_pct,wind_kmh,solar_wm2)"
        " VALUES (?,?,?,?,?,?)",
        [(zone_id, r["time"], r["temp_c"], r["rh_pct"], r["wind_kmh"], r["solar_wm2"])
         for r in rows],
    )
    conn.commit()
    return len(rows)


def load_hourly(conn: sqlite3.Connection, zone_id: str) -> list:
    cur = conn.execute(
        "SELECT time,temp_c,rh_pct,wind_kmh,solar_wm2 FROM hourly"
        " WHERE zone_id=? ORDER BY time", (zone_id,))
    return [{"time": t, "temp_c": te, "rh_pct": rh, "wind_kmh": w, "solar_wm2": s}
            for t, te, rh, w, s in cur.fetchall()]


def zone_counts(conn: sqlite3.Connection) -> dict:
    return {z: c for z, c in
            conn.execute("SELECT zone_id,COUNT(*) FROM hourly GROUP BY zone_id")}
