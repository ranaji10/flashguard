#!/usr/bin/env bash
# Keep the verifier contract and corpus verdict-gap checks visible in the suite.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"

if [ ! -f "$ROOT/flashguard/verify.py" ]; then
  echo "  VERIFIER NOT IMPLEMENTED: flashguard/verify.py is absent"
  echo "      Contract tests are present but cannot run until the first verifier exists."
  exit 2
fi

# Until 17 Oct only the last line's result reached all.sh: a failure in any earlier file
# was printed and then ignored. Each file now fails the run on its own.
fail=0
for t in test_verify_contract.py test_verdict_gap.py test_verify_v2.py test_false_safe_gate.py \
         test_verdict_v03.py test_rulings_2026_10_08.py test_absence_rule_2026_10_17.py \
         test_unlock_route_withdrawn.py; do
  python3 "$HERE/$t" || { echo "  FAIL in $t"; fail=1; }
done
exit $fail
