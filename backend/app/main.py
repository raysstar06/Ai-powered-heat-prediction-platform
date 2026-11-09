"""FastAPI backend: zones, current/forecast risk, advisory, municipal, healthcare."""
import json
import sqlite3
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

APP_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(APP_DIR))

import advisory
import history as hist
import risk as riskmod
import thermal
from config import load_zones

BASE = APP_DIR.parent
DB = BASE / "data" / "cache.sqlite"
HISTORY_JSON = BASE / "data" / "history.json"
COOLING_JSON = BASE / "data" / "cooling_centers.json"

app = FastAPI(title="Heat Early Warning API")
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["GET"], allow_headers=["*"])

ZONES = {z["zone_id"]: z for z in load_zones()}
HISTORY = json.loads(HISTORY_JSON.read_text())
POIS = json.loads(COOLING_JSON.read_text())
MODEL = None


def get_model():
    global MODEL
    if MODEL is None:
        import joblib
        MODEL = joblib.load(BASE / "models" / "model.pkl")
    return MODEL


def latest(zone_id: str) -> dict:
    conn = sqlite3.connect(str(DB))
    cur = conn.execute(
        "SELECT time,temp_c,rh_pct,wind_kmh,solar_wm2 FROM hourly"
        " WHERE zone_id=? ORDER BY time DESC LIMIT 1", (zone_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        raise HTTPException(404, f"no cached data for {zone_id}")
    return {"time": row[0], "temp_c": row[1], "rh_pct": row[2],
            "wind_kmh": row[3], "solar_wm2": row[4]}


def recent(zone_id: str, n: int = 48) -> list:
    conn = sqlite3.connect(str(DB))
    cur = conn.execute(
        "SELECT time,temp_c,rh_pct,wind_kmh,solar_wm2 FROM hourly"
        " WHERE zone_id=? ORDER BY time DESC LIMIT ?", (zone_id, n))
    rows = [{"time": r[0], "temp_c": r[1], "rh_pct": r[2],
             "wind_kmh": r[3], "solar_wm2": r[4]} for r in cur.fetchall()]
    conn.close()
    return list(reversed(rows))


def normalize(zone_id: str, wbgt: float) -> dict:
    z = ZONES[zone_id]
    d = HISTORY[zone_id]
    thermal_n = max(0.0, min(1.0, (wbgt - 25.0) / 10.0))
    anomaly_n = 1.0 if wbgt > d["p90"] else (0.5 if wbgt > d["p75"] else 0.2)
    spatial_n = max(0.0, min(1.0, float(z["lst_offset_c"]) / 2.5))
    vulner_n = max(0.0, min(1.0, (float(z["pop_density"]) / 12500.0 * 0.5
                                  + float(z["elderly_share"]) / 0.12 * 0.5)))
    return {"thermal": thermal_n, "anomaly": anomaly_n,
            "spatial": spatial_n, "vulner": vulner_n}


@app.get("/")
def root():
    return {"app": "Heat Early Warning API",
            "docs": "/docs", "health": "/health", "zones": "/zones"}


@app.get("/health")
def health():
    conn = sqlite3.connect(str(DB))
    n = conn.execute("SELECT COUNT(*) FROM hourly").fetchone()[0]
    conn.close()
    return {"ok": True, "cached_rows": n, "zones": len(ZONES)}


@app.get("/zones")
def zones():
    return [{"zone_id": z, **{k: ZONES[z][k] for k in
                              ("name", "lat", "lon", "lst_offset_c",
                               "pop_density", "elderly_share")}}
            for z in ZONES]


@app.get("/risk/current")
def risk_current(zone: str = Query(...)):
    if zone not in ZONES:
        raise HTTPException(404, "unknown zone")
    cur = latest(zone)
    wbgt = thermal.wbgt_c(cur["temp_c"], cur["rh_pct"])
    hi = thermal.heat_index_c(cur["temp_c"], cur["rh_pct"])
    parts = normalize(zone, wbgt)
    r = riskmod.risk_parts(**parts)
    d = HISTORY[zone]
    return {"zone": zone, "time": cur["time"],
            "temp_c": cur["temp_c"], "rh_pct": cur["rh_pct"],
            "wbgt": round(wbgt, 2), "heat_index": round(hi, 2),
            "percentiles": d, "unusual": hist.is_unusual(wbgt, d),
            "risk": r}


@app.get("/risk/forecast")
def risk_forecast(zone: str = Query(...)):
    if zone not in ZONES:
        raise HTTPException(404, "unknown zone")
    import pandas as pd
    import predict as predictor
    rows = recent(zone, 48)
    if len(rows) < 24:
        raise HTTPException(503, "not enough cached hours")
    fc = predictor.forecast(zone, pd.DataFrame(rows))
    vals = [fc["+24h"], fc["+48h"], fc["+72h"]]
    top = max(vals)
    parts = normalize(zone, top)
    r = riskmod.risk_parts(**parts)
    return {"zone": zone, "forecast_wbgt": fc,
            "risk": r,
            "degree_hours": riskmod.degree_hours(vals)}


@app.get("/advisory")
def get_advisory(zone: str = Query(...),
                 age: int = 30, weight: float = 60.0,
                 activity: str = "rest", duration_min: int = 30,
                 exertion: str = "light"):
    cur = risk_current(zone)
    a = advisory.advise(age, weight, activity, duration_min,
                        exertion, cur["risk"]["band"])
    return {"zone": zone, "band": cur["risk"]["band"],
            "wbgt": cur["wbgt"], "advisory": a}


@app.get("/municipal")
def municipal():
    ranked = []
    for z in ZONES:
        cur = latest(z)
        wbgt = thermal.wbgt_c(cur["temp_c"], cur["rh_pct"])
        r = riskmod.risk_parts(**normalize(z, wbgt))
        ranked.append({"zone": z, "name": ZONES[z]["name"],
                       "wbgt": round(wbgt, 2), "score": r["score"],
                       "band": r["band"],
                       "lst_offset_c": ZONES[z]["lst_offset_c"],
                       "pois": POIS.get(z, [])})
    ranked.sort(key=lambda x: -x["score"])
    return {"ranking": ranked}


@app.get("/healthcare")
def healthcare():
    import pandas as pd
    import predict as predictor
    zones_out, vuln = [], []
    for z in ZONES:
        rows = recent(z, 48)
        if len(rows) < 24:
            continue
        fc = predictor.forecast(z, pd.DataFrame(rows))
        vals = [fc["+24h"], fc["+48h"], fc["+72h"]]
        zones_out.append({"zone": z, "name": ZONES[z]["name"],
                          "forecast_wbgt": fc,
                          "degree_hours": riskmod.degree_hours(vals)})
        vuln.append((z, float(ZONES[z]["elderly_share"])))
    vuln.sort(key=lambda x: -x[1])
    return {"zones": zones_out,
            "vulnerable_first": [z for z, _ in vuln]}
