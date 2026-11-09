#!/bin/sh
# Demo-day smoke test. Usage: ./scripts/smoke.sh [BASE_URL]
BASE="${1:-http://127.0.0.1:8000}"
pass=0; fail=0
check() {
  desc="$1"; shift
  if curl -sf "$@" >/dev/null; then echo "PASS: $desc"; pass=$((pass+1));
  else echo "FAIL: $desc"; fail=$((fail+1)); fi
}
check "health" "$BASE/health"
check "zones" "$BASE/zones"
check "current central" "$BASE/risk/current?zone=central"
check "current hinjawadi" "$BASE/risk/current?zone=hinjawadi-it"
check "forecast central" "$BASE/risk/forecast?zone=central"
check "advisory young-light" "$BASE/advisory?zone=central&age=25&activity=rest&duration_min=10&exertion=light"
check "advisory elderly-heavy" "$BASE/advisory?zone=central&age=70&activity=outdoor_work&duration_min=240&exertion=heavy"
check "municipal" "$BASE/municipal"
check "readiness" "$BASE/readiness"
echo "--- $pass passed, $fail failed ---"
[ "$fail" -eq 0 ]
