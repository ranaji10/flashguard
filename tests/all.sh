#!/usr/bin/env bash
# Everything that can be checked without a device. Run before every commit.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
soft=0
echo; echo "  PORTABILITY"; bash "$HERE/check-portability.sh" || exit 1
echo; echo "  PARSE"; bash "$HERE/check-console.sh" || exit 1
if command -v node >/dev/null 2>&1; then
  echo "  CONSOLE LOGIC"; node "$HERE/run-console-logic.js" || exit 1
fi
echo; echo "  CLASSIFIER"; bash "$HERE/run.sh" || exit 1
echo "  WEBUSB ROUTE AGREEMENT"; bash "$HERE/test-webusb-agreement.sh" || exit 1
echo "  ANDROID DERIVATION"; bash "$HERE/run-android.sh" || exit 1
echo "  ANDROID RAW AGREEMENT"; bash "$HERE/test-android-raw-agreement.sh" || exit 1
echo "  VERIFIER"
bash "$HERE/run-verify.sh"; rc=$?
[ "$rc" = 1 ] && exit 1
[ "$rc" = 2 ] && { echo "  ^ not build-failing, but verifier implementation is still required"; soft=1; }
echo "  RECIPES"
python3 "$HERE/check-recipes.py" || exit 1
python3 "$HERE/check-recipes.py" --self-test || exit 1
echo "  PREREQUISITE SURVEY"
python3 "$HERE/test_prerequisite_survey.py" || exit 1
echo "  DISPUTED"
bash "$HERE/check-disputed.sh"; rc=$?
[ "$rc" = 2 ] && soft=1
[ "$rc" = 2 ] || echo "  no open disagreements"
echo "  INDEX"
bash "$HERE/check-index.sh"; rc=$?
[ "$rc" = 1 ] && exit 1
[ "$rc" = 2 ] && { echo "  ^ not build-failing, but recruitment cannot start"; soft=1; }
echo "  TRACKER"; bash "$HERE/check-tracker.sh" || exit 1
echo "  PACKAGE"; bash "$HERE/check-package.sh" || exit 1
echo "  INTAKE"; python3 "$HERE/test_intake.py" || exit 1
python3 "$HERE/test_derive_pending.py" || exit 1
echo "  WHAT WOULD GO PUBLIC"; bash "$HERE/check-public-safe.sh" || exit 1
echo "  DESCRIPTOR PRIVACY"; bash "$HERE/check-descriptor-privacy.sh" || exit 1
python3 "$HERE/test_contributions_validation.py" || exit 1
echo "  DATA"; python3 "$HERE/../data/merge.py" --check >/dev/null 2>&1 \
  && echo "  contributions validate" || echo "  contributions have problems, run data/merge.py --check"
[ "$soft" = 1 ] && exit 2
echo
