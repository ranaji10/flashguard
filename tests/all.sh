#!/usr/bin/env bash
# Everything that can be checked without a device. Run before every commit.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
echo; echo "  PARSE"; bash "$HERE/check-console.sh" || exit 1
echo; echo "  CLASSIFIER"; bash "$HERE/run.sh" || exit 1
echo "  DATA"; python3 "$HERE/../data/merge.py" --check >/dev/null 2>&1 \
  && echo "  contributions validate" || echo "  contributions have problems, run data/merge.py --check"
echo
