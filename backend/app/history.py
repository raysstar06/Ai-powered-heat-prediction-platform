"""History percentiles: pure-python p50/p75/p90 + anomaly flag."""


def percentile(sorted_vals: list, pct: float) -> float:
    if not sorted_vals:
        return 0.0
    vals = sorted(sorted_vals)
    k = (len(vals) - 1) * (pct / 100.0)
    f, c = int(k), min(int(k) + 1, len(vals) - 1)
    return vals[f] + (vals[c] - vals[f]) * (k - f)


def distribution(values: list) -> dict:
    return {"p50": round(percentile(values, 50), 2),
            "p75": round(percentile(values, 75), 2),
            "p90": round(percentile(values, 90), 2),
            "n": len(values)}


def is_unusual(current: float, dist: dict) -> bool:
    return current > dist.get("p90", float("inf"))
