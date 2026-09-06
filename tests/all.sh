#!/usr/bin/env bash
# Everything that can be checked without a device. Run before every commit.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
echo; echo "  PORTABILITY"; bash "$HERE/check-portability.sh" || exit 1
echo; echo "  PARSE"; bash "$HERE/check-console.sh" || exit 1
if command -v node >/dev/null 2>&1; then
  echo "  CONSOLE LOGIC"; node "$HERE/run-console-logic.js" || exit 1
fi
echo; echo "  CLASSIFIER"; bash "$HERE/run.sh" || exit 1
echo "  ANDROID DERIVATION"; bash "$HERE/run-android.sh" || exit 1
echo "  INDEX"
bash "$HERE/check-index.sh"; rc=$?
[ "$rc" = 1 ] && exit 1
[ "$rc" = 2 ] && echo "  ^ not build-failing, but recruitment cannot start"
echo "  DESCRIPTOR PRIVACY"; bash "$HERE/check-descriptor-privacy.sh" || exit 1
echo "  DATA"; python3 "$HERE/../data/merge.py" --check >/dev/null 2>&1 \
  && echo "  contributions validate" || echo "  contributions have problems, run data/merge.py --check"
echo
