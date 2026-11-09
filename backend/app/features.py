"""ML features: lagged/rolling WBGT + recent weather + time + zone spatial."""
import math

import pandas as pd


def add_wbgt(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    e = (df["rh_pct"] / 100.0) * 6.105 * (17.27 * df["temp_c"] / (237.7 + df["temp_c"])).apply(math.exp)
    df["wbgt"] = 0.567 * df["temp_c"] + 0.393 * e + 3.94
    return df


def make_supervised(df: pd.DataFrame, horizons=(24, 48, 72)) -> pd.DataFrame:
    """One row per zone+hour with lag features and shift targets."""
    df = df.copy()
    df["time"] = pd.to_datetime(df["time"])
    df = df.sort_values(["zone_id", "time"])
    for lag in (1, 3, 6, 24):
        df[f"wbgt_lag{lag}"] = df.groupby("zone_id")["wbgt"].shift(lag)
    df["wbgt_roll6"] = df.groupby("zone_id")["wbgt"].transform(
        lambda s: s.shift(1).rolling(6).mean())
    df["wbgt_roll24"] = df.groupby("zone_id")["wbgt"].transform(
        lambda s: s.shift(1).rolling(24).mean())
    df["hour"] = df["time"].dt.hour
    df["dayofyear"] = df["time"].dt.dayofyear
    for h in horizons:
        df[f"target_{h}h"] = df.groupby("zone_id")["wbgt"].shift(-h)
    return df.dropna().reset_index(drop=True)


FEATURE_COLS = ["temp_c", "rh_pct", "wind_kmh", "solar_wm2", "lst_offset_c",
                "wbgt_lag1", "wbgt_lag3", "wbgt_lag6", "wbgt_lag24",
                "wbgt_roll6", "wbgt_roll24", "hour", "dayofyear"]
