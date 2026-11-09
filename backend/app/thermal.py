"""Thermal Stress Engine — pure physics, no vulnerability here.

Rule: vulnerability changes RANKING only, never the WBGT value.
Formulas are prototype approximations, disclosed in docs/video.
"""
import math


def vapour_pressure_hpa(temp_c: float, rh_pct: float) -> float:
    rh = max(0.0, min(100.0, rh_pct))
    return (rh / 100.0) * 6.105 * math.exp(17.27 * temp_c / (237.7 + temp_c))


def wbgt_c(temp_c: float, rh_pct: float) -> float:
    """Simplified outdoor WBGT approximation (BOM-style).

    WBGT = 0.567*T + 0.393*e + 3.94, e = vapour pressure in hPa.
    No black-globe temp in prototype; solar/wind enter the risk layer.
    """
    e = vapour_pressure_hpa(temp_c, rh_pct)
    return 0.567 * temp_c + 0.393 * e + 3.94


def heat_index_c(temp_c: float, rh_pct: float) -> float:
    """Rothfusz Heat Index, computed in F then back to C. Secondary display only."""
    tf = temp_c * 9.0 / 5.0 + 32.0
    rh = max(0.0, min(100.0, rh_pct))
    if tf < 80:
        hi_f = 0.5 * (tf + 61.0 + ((tf - 68.0) * 1.2) + (rh * 0.094))
        hi_f = (hi_f + tf) / 2.0 if hi_f < 80 else hi_f
    else:
        hi_f = (-42.379 + 2.04901523 * tf + 10.14333127 * rh
                - 0.22475541 * tf * rh - 0.00683783 * tf * tf
                - 0.05481717 * rh * rh + 0.00122874 * tf * tf * rh
                + 0.00085282 * tf * rh * rh - 0.00000199 * tf * tf * rh * rh)
        if rh < 13 and 80 <= tf <= 112:
            hi_f -= ((13 - rh) / 4.0) * math.sqrt((17 - abs(tf - 95.0)) / 17.0)
        elif rh > 85 and 80 <= tf <= 87:
            hi_f += ((rh - 85) / 10.0) * ((87 - tf) / 5.0)
    return (hi_f - 32.0) * 5.0 / 9.0
