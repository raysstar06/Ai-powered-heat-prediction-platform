"""Citizen advisory rules. General guidance only, not medical advice."""
DISCLAIMER = "General heat-safety guidance, not a medical diagnosis."


def advise(age: int, weight_kg: float, activity: str, duration_min: int,
           exertion: str, band: str) -> dict:
    activity = (activity or "rest").lower()
    exertion = (exertion or "light").lower()
    heavy = activity in ("outdoor_work", "construction", "sports") or exertion == "heavy"
    vulnerable = age >= 60 or age <= 5

    base_water = max(0.25, (weight_kg or 60) * 0.01 * max(0.25, duration_min / 60.0))
    if band in ("High", "Extreme"):
        base_water *= 1.5
    if heavy:
        base_water *= 1.25

    if band == "Low":
        rest = "No extra breaks needed. Rest in shade if tired."
    elif band == "Moderate":
        rest = "10 min shade break every hour. Avoid 12-3pm heavy work."
    elif band == "High":
        rest = "15 min shade break every 30-45 min. Shift heavy work to morning/evening."
    else:
        rest = "Avoid outdoor exertion 11am-4pm. Work 15 min / rest 15 min in shade if must."

    if vulnerable or band == "Extreme":
        rest += " Extra care: elderly/children overheat faster."

    return {
        "water_litres": round(base_water, 2),
        "drink_every_min": 20 if band in ("High", "Extreme") or heavy else 30,
        "work_rest": rest,
        "cooling": "Cool shower, wet cloth on neck, fan + shade, ORS if sweating a lot.",
        "warning_signs": ("Heat exhaustion: heavy sweat, weakness, headache, nausea. "
                          "Heatstroke: hot/dry skin, confusion, fainting — call emergency."),
        "disclaimer": DISCLAIMER,
    }
