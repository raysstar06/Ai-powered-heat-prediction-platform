"""Risk engine: explainable 0-100 score. Vulnerability ranks, never changes WBGT."""
def band_for(score: float) -> str:
    for limit, name in ((25, "Low"), (50, "Moderate"), (75, "High"), (101, "Extreme")):
        if score < limit:
            return name
    return "Extreme"


def risk_score(thermal: float, anomaly: float, spatial: float, vulner: float) -> float:
    """All inputs 0-1. Weights fixed for prototype: 0.45/0.20/0.15/0.20."""
    parts = [thermal * 0.45, anomaly * 0.20, spatial * 0.15, vulner * 0.20]
    return round(sum(parts) * 100.0, 1)


def risk_parts(thermal: float, anomaly: float, spatial: float, vulner: float) -> dict:
    score = risk_score(thermal, anomaly, spatial, vulner)
    return {
        "score": score,
        "band": band_for(score),
        "parts": {
            "thermal_hazard": round(thermal * 45.0, 1),
            "historical_anomaly": round(anomaly * 20.0, 1),
            "spatial_uhi": round(spatial * 15.0, 1),
            "vulnerability": round(vulner * 20.0, 1),
        },
    }


def degree_hours(forecast_wbgt: list, threshold: float = 30.0) -> float:
    """Consecutive High-Risk Degree-Hours: sum of (wbgt-threshold) while above."""
    total, run = 0.0, 0.0
    peak = 0.0
    for v in forecast_wbgt:
        if v > threshold:
            run += max(0.0, v - threshold)
            peak = max(peak, run)
        else:
            run = 0.0
    total = peak
    return round(total, 2)
