"""Inference: load model.pkl, forecast 24/48/72h WBGT for one zone."""
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND / "app"))

import joblib
import pandas as pd

from config import load_zones
from features import FEATURE_COLS, add_wbgt

BUNDLE = BACKEND / "models" / "model.pkl"


def forecast(zone_id: str, recent: pd.DataFrame) -> dict:
    """recent: hourly rows with time,temp_c,rh_pct,wind_kmh,solar_wm2 (oldest first)."""
    bundle = joblib.load(BUNDLE)
    zones = {z["zone_id"]: z for z in load_zones()}
    df = recent.copy()
    df["zone_id"] = zone_id
    df["lst_offset_c"] = float(zones[zone_id]["lst_offset_c"])
    df = add_wbgt(df)
    df["time"] = pd.to_datetime(df["time"])
    df = df.sort_values("time").reset_index(drop=True)
    last = df.iloc[-1]
    row = {"temp_c": last["temp_c"], "rh_pct": last["rh_pct"],
           "wind_kmh": last["wind_kmh"], "solar_wm2": last["solar_wm2"],
           "lst_offset_c": last["lst_offset_c"],
           "wbgt_lag1": df["wbgt"].iloc[-1], "wbgt_lag3": df["wbgt"].iloc[-3],
           "wbgt_lag6": df["wbgt"].iloc[-6], "wbgt_lag24": df["wbgt"].iloc[-24],
           "wbgt_roll6": df["wbgt"].iloc[-6:].mean(),
           "wbgt_roll24": df["wbgt"].iloc[-24:].mean(),
           "hour": pd.Timestamp(last["time"]).hour,
           "dayofyear": pd.Timestamp(last["time"]).dayofyear}
    X = pd.DataFrame([row])[FEATURE_COLS]
    return {f"+{h}h": round(float(bundle["models"][f"h{h}"].predict(X)[0]), 2)
            for h in (24, 48, 72)}
