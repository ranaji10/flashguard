#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Replay every saved USB descriptor through the classifier and compare the
# result with the class recorded in the fixture's `#!expect=` header.
#
# No device is needed and nothing is plugged in. Runs in about a second.
# Run it before every commit that touches classify.sh.
#
#   bash tests/run.sh            all fixtures
#   bash tests/run.sh samsung    fixtures whose name matches
#
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
CLASSIFY="$HERE/../bench-kit/scripts/classify.sh"
FILTER="${1:-}"

pass=0; fail=0; skip=0
printf '\n  %-42s %-14s %-14s %s\n' FIXTURE EXPECTED GOT ""
printf '  %s\n' "$(printf '%.0s-' $(seq 1 84))"

for f in "$HERE"/fixtures/*.desc; do
  [ -e "$f" ] || continue
  name=$(basename "$f" .desc)
  [ -n "$FILTER" ] && case "$name" in *"$FILTER"*) ;; *) continue;; esac
  want=$(sed -n 's/^#!expect=//p' "$f" | head -1)
  if [ -z "$want" ]; then
    printf '  %-42s %-14s %-14s %s\n' "$name" "-" "-" "SKIP no #!expect header"
    skip=$((skip+1)); continue
  fi
  got=$(ADB_STATE="" bash "$CLASSIFY" < "$f" | awk -F'\t' '$1=="class"{print $2}')
  if [ "$got" = "$want" ]; then
    printf '  %-42s %-14s %-14s %s\n' "$name" "$want" "$got" "ok"
    pass=$((pass+1))
  else
    printf '  %-42s %-14s %-14s %s\n' "$name" "$want" "$got" "FAIL"
    fail=$((fail+1))
  fi
done

echo
echo "  $pass passed, $fail failed, $skip skipped"
if [ "$fail" -gt 0 ]; then
  echo
  echo "  A failure here is the classifier disagreeing with a device whose identity"
  echo "  a human established independently. Fix classify.sh, not the fixture --"
  echo "  unless the fixture's expected class was itself wrong, in which case say so"
  echo "  in a #!note and record why."
  echo
  exit 1
fi
echo
