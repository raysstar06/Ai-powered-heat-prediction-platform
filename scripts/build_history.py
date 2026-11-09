"""Build per-zone WBGT history (p50/p75/p90) from archive. Run once, save JSON."""
import csv
import json
import math
import urllib.parse
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
ZONES_CSV = BASE / "backend" / "data" / "zones.csv"
OUT = BASE / "backend" / "data" / "history.json"

VARS = "temperature_2m,relative_humidity_2m"
START, END = "2024-03-01", "2024-06-30"


def wbgt(t, rh):
    rh = max(0.0, min(100.0, rh))
    e = (rh / 100.0) * 6.105 * math.exp(17.27 * t / (237.7 + t))
    return 0.567 * t + 0.393 * e + 3.94


def pct(sorted_vals, p):
    if not sorted_vals:
        return 0.0
    k = (len(sorted_vals) - 1) * (p / 100.0)
    f, c = int(k), min(int(k) + 1, len(sorted_vals) - 1)
    return sorted_vals[f] + (sorted_vals[c] - sorted_vals[f]) * (k - f)


def main():
    out = {}
    for row in csv.DictReader(ZONES_CSV.open()):
        params = {"latitude": row["lat"], "longitude": row["lon"],
                  "hourly": VARS, "start_date": START, "end_date": END,
                  "timezone": "Asia/Kolkata"}
        url = ("https://archive-api.open-meteo.com/v1/archive?"
               + urllib.parse.urlencode(params))
        with urllib.request.urlopen(url, timeout=60) as r:
            h = json.loads(r.read().decode())["hourly"]
        vals = sorted(wbgt(t, rh) for t, rh in
                      zip(h["temperature_2m"], h["relative_humidity_2m"]))
        out[row["zone_id"]] = {"p50": round(pct(vals, 50), 2),
                               "p75": round(pct(vals, 75), 2),
                               "p90": round(pct(vals, 90), 2),
                               "n": len(vals)}
        print(row["zone_id"], out[row["zone_id"]])
    OUT.write_text(json.dumps(out, indent=2))
    print(f"saved {OUT.name}")


if __name__ == "__main__":
    main()
