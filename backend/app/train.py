"""Train zone WBGT forecast models (24/48/72h). Run with the project venv.

Compares persistence baseline vs RandomForest (+XGBoost if libomp present).
Saves backend/models/model.pkl and metrics.json.
"""
import csv
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND / "app"))

import joblib
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from config import load_zones
from features import FEATURE_COLS, add_wbgt, make_supervised

try:
    from xgboost import XGBRegressor
    HAS_XGB = True
except Exception:
    HAS_XGB = False

ARCHIVE = "https://archive-api.open-meteo.com/v1/archive"
VARS = "temperature_2m,relative_humidity_2m,wind_speed_10m,shortwave_radiation"
START, END = "2024-03-01", "2024-06-30"  # full pre-monsoon + onset for Pune


def fetch_history(lat, lon):
    params = {"latitude": lat, "longitude": lon, "hourly": VARS,
              "start_date": START, "end_date": END, "timezone": "Asia/Kolkata"}
    url = ARCHIVE + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=60) as r:
        return json.loads(r.read().decode())["hourly"]


def load_frame() -> pd.DataFrame:
    zones = {z["zone_id"]: z for z in load_zones()}
    frames = []
    for zid, z in zones.items():
        h = fetch_history(z["lat"], z["lon"])
        f = pd.DataFrame({"time": h["time"], "temp_c": h["temperature_2m"],
                          "rh_pct": h["relative_humidity_2m"],
                          "wind_kmh": h["wind_speed_10m"],
                          "solar_wm2": h["shortwave_radiation"]})
        f["zone_id"] = zid
        f["lst_offset_c"] = float(z["lst_offset_c"])
        frames.append(f)
    df = pd.concat(frames, ignore_index=True)
    return make_supervised(add_wbgt(df))


def chrono_split(df, train=0.7, val=0.15):
    df = df.sort_values("time").reset_index(drop=True)
    n = len(df)
    i, j = int(n * train), int(n * (train + val))
    return df.iloc[:i], df.iloc[i:j], df.iloc[j:]


def scores(y, p):
    return {"MAE": round(float(mean_absolute_error(y, p)), 3),
            "RMSE": round(float(mean_squared_error(y, p)) ** 0.5, 3),
            "R2": round(float(r2_score(y, p)), 3)}


def main():
    df = load_frame()
    print(f"rows: {len(df)} cols ok")
    tr, va, te = chrono_split(df)
    Xtr, Xva, Xte = tr[FEATURE_COLS], va[FEATURE_COLS], te[FEATURE_COLS]
    models, metrics = {}, {}
    for h in (24, 48, 72):
        ytr, yva, yte = tr[f"target_{h}h"], va[f"target_{h}h"], te[f"target_{h}h"]
        # persistence baseline: carry forward last observed WBGT
        m = {"persistence": scores(yte, te["wbgt_lag1"])}
        rf = RandomForestRegressor(n_estimators=200, min_samples_leaf=5,
                                   n_jobs=-1, random_state=7)
        rf.fit(Xtr, ytr)
        m["random_forest"] = scores(yte, rf.predict(Xte))
        hgb = HistGradientBoostingRegressor(max_iter=300, learning_rate=0.06,
                                            random_state=7)
        hgb.fit(Xtr, ytr)
        m["gradient_boosting"] = scores(yte, hgb.predict(Xte))
        best, best_name = (rf, "random_forest") if (
            m["random_forest"]["MAE"] <= m["gradient_boosting"]["MAE"]
        ) else (hgb, "gradient_boosting")
        if HAS_XGB:
            xgb = XGBRegressor(n_estimators=300, max_depth=6, learning_rate=0.05,
                               subsample=0.8, n_jobs=-1, random_state=7)
            xgb.fit(Xtr, ytr)
            m["xgboost"] = scores(yte, xgb.predict(Xte))
            if m["xgboost"]["MAE"] < m["random_forest"]["MAE"]:
                best, best_name = xgb, "xgboost"
        models[f"h{h}"] = best
        metrics[f"h{h}"] = m
        print(f"+{h}h winner={best_name} {m[best_name]} (persist {m['persistence']})")
    out = BACKEND / "models"
    out.mkdir(exist_ok=True)
    joblib.dump({"models": models, "features": FEATURE_COLS,
                 "xgb_available": HAS_XGB}, out / "model.pkl")
    (out / "metrics.json").write_text(json.dumps(metrics, indent=2))
    print(f"saved model.pkl + metrics.json (xgb_available={HAS_XGB})")


if __name__ == "__main__":
    main()
