"""Advisory corner-case checks. Run with system python3 (stdlib only)."""
import importlib.util

spec = importlib.util.spec_from_file_location(
    "advisory", "heat-platform/backend/app/advisory.py")
a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)

CASES = {
    "reported_elderly": dict(age=65, weight_kg=62, activity="outdoor_work",
                              duration_min=240, exertion="heavy"),
    "young_light_same_band": dict(age=30, weight_kg=70, activity="rest",
                                   duration_min=60, exertion="light"),
    "infant": dict(age=3, weight_kg=15, activity="rest",
                   duration_min=30, exertion="light"),
    "extreme_elderly": dict(age=80, weight_kg=70, activity="outdoor_work",
                             duration_min=480, exertion="heavy"),
    "athlete": dict(age=25, weight_kg=70, activity="sports",
                    duration_min=120, exertion="heavy"),
    "office": dict(age=40, weight_kg=75, activity="rest",
                   duration_min=30, exertion="light"),
}

BAND = {"reported_elderly": "Moderate", "young_light_same_band": "Moderate",
        "infant": "Low", "extreme_elderly": "Extreme",
        "athlete": "High", "office": "Low"}

fails = []


def check(name, cond, detail):
    print(("PASS " if cond else "FAIL ") + name + " | " + str(detail))
    if not cond:
        fails.append(name)


res = {n: a.advise(band=BAND[n], **{k: v for k, v in c.items()}) for n, c in CASES.items()}
for n, r in res.items():
    print(f"  {n}: water={r['water_litres']}L every={r['drink_every_min']}m band={BAND[n]}")

# The reported case: mild heat (Moderate) must not prescribe >2.5L
check("reported_water_sane", res["reported_elderly"]["water_litres"] <= 2.5,
      res["reported_elderly"]["water_litres"])
# Same band, very different people => different rest guidance
check("personalized_rest",
      res["reported_elderly"]["work_rest"] != res["young_light_same_band"]["work_rest"],
      "elderly-heavy-4h vs young-light-1h")
# Hourly intake never exceeds 1.0 L/h for any case
for n, c in CASES.items():
    hourly = res[n]["water_litres"] / max(c["duration_min"] / 60.0, 0.25)
    check(f"hourly_cap[{n}]", hourly <= 1.0 + 1e-9, round(hourly, 2))
# Intervals from a sane set
for n, r in res.items():
    check(f"interval[{n}]", r["drink_every_min"] in (15, 20, 30, 45, 60),
          r["drink_every_min"])
# Vulnerable people get the extra-care note
for n in ("reported_elderly", "infant", "extreme_elderly"):
    check(f"vulnerable_note[{n}]", "Extra care" in res[n]["work_rest"], True)

print("FAILURES:", fails if fails else "none")
raise SystemExit(1 if fails else 0)
