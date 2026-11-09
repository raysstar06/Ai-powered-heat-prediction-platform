"""Citizen advisory rules. General guidance only, not medical advice.

Water scales with heat band first, then duration, exertion, vulnerability.
Hourly intake is capped at 1.0 L/h. Rest strictness follows a strain score
(band + heavy exertion + long duration + vulnerability), so the same band
can still give very different guidance to different people.
"""
DISCLAIMER = "General heat-safety guidance, not a medical diagnosis."

BAND_LEVEL = {"Low": 0, "Moderate": 1, "High": 2, "Extreme": 3}
BASE_RATE_LPH = {0: 0.15, 1: 0.30, 2: 0.60, 3: 0.90}  # litres/hour by heat
MAX_LPH = 1.0
MAX_TOTAL_L = 6.0
MIN_TOTAL_L = 0.25

REST = {
    "relaxed": "No extra breaks needed. Rest in shade if tired.",
    "cautious": "10 min shade break every hour. Avoid 12-3pm heavy work.",
    "strict": "15 min shade break every 30-45 min. Shift heavy work to morning/evening.",
    "severe": "Avoid outdoor exertion 11am-4pm. Work 15 min / rest 15 min in shade if must.",
}


def advise(age: int, weight_kg: float, activity: str, duration_min: int,
           exertion: str, band: str) -> dict:
    activity = (activity or "rest").lower()
    exertion = (exertion or "light").lower()
    heavy = activity in ("outdoor_work", "construction", "sports") or exertion == "heavy"
    vulnerable = age >= 60 or age <= 5

    level = BAND_LEVEL.get(band, 1)
    strain = level + (1 if heavy else 0) + (1 if duration_min >= 120 else 0) \
        + (1 if duration_min >= 240 else 0) + (1 if vulnerable else 0)
    tier = "relaxed" if strain <= 1 else "cautious" if strain == 2 \
        else "strict" if strain == 3 else "severe"
    rest = REST[tier]
    if vulnerable:
        rest += " Extra care: elderly/children overheat faster."

    rate = BASE_RATE_LPH[level]
    if heavy:
        rate *= 1.3
    if vulnerable:
        rate *= 1.2
    rate = min(rate, MAX_LPH)
    water = max(MIN_TOTAL_L, min(rate * max(duration_min, 15) / 60.0, MAX_TOTAL_L))

    interval = 15 if rate >= 0.8 else 20 if rate >= 0.5 else 30 \
        if rate >= 0.3 else 45 if rate >= 0.2 else 60

    return {
        "water_litres": round(water, 2),
        "drink_every_min": interval,
        "work_rest": rest,
        "level": tier,
        "cooling": "Cool shower, wet cloth on neck, fan + shade, ORS if sweating a lot.",
        "warning_signs": ("Heat exhaustion: heavy sweat, weakness, headache, nausea. "
                          "Heatstroke: hot/dry skin, confusion, fainting — call emergency."),
        "disclaimer": DISCLAIMER,
    }
