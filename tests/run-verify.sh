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

python3 "$HERE/test_verify_contract.py"
python3 "$HERE/test_verdict_gap.py"
python3 "$HERE/test_verify_v2.py"
python3 "$HERE/test_false_safe_gate.py"
