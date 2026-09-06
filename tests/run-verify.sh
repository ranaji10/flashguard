#!/usr/bin/env bash
# The verifier is intentionally absent until its first implementation lands.
# Keep that absence visible without making unrelated checks look green.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"

if [ ! -f "$ROOT/verify.py" ]; then
  echo "  VERIFIER NOT IMPLEMENTED: verify.py is absent"
  echo "      Contract tests are present but cannot run until the first verifier exists."
  exit 2
fi

python3 "$HERE/test_verify_contract.py"
