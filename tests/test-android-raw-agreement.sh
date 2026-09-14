#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Prove that property-key ordering is transparent to derive.sh, and prove that
# un-normalised input hazards (CRLF, leading whitespace, bare values) genuinely
# break derivation when unhandled — establishing that normalisation is load-bearing.
#
# The normaliser itself (normaliseRawProps, isValidRawProps) is tested in Node.js
# via tests/run-console-logic.js against all fixtures.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
DERIVE="$HERE/../bench-kit/scripts/derive.sh"
fail=0

printf '\n  %-34s %-24s %s\n' "FIXTURE" "CONDITION TESTED" "RESULT"
printf '  %s\n' "$(printf '%.0s-' $(seq 1 72))"

for f in "$HERE"/android/*.props; do
  [ -e "$f" ] || continue
  name=$(basename "$f" .props)

  bash_raw=$(grep -v '^#!' "$f")
  bash_derived=$(printf '%s\n' "$bash_raw" | bash "$DERIVE")

  # 1. Shuffled key order is transparent (must match canonical)
  shuffled_input=$(printf '%s\n' "$bash_raw" | sort -r)
  shuffled_derived=$(printf '%s\n' "$shuffled_input" | bash "$DERIVE")
  if [ "$shuffled_derived" = "$bash_derived" ]; then
    printf '  %-34s %-24s %s\n' "$name" "shuffled key order" "ok"
  else
    printf '  %-34s %-24s %s\n' "$name" "shuffled key order" "FAIL"
    fail=1
  fi

  # For fixtures that contain real property values, assert that un-normalised hazards
  # produce DIFFERENT derivation output, proving the hazards are real.
  if [ "$name" != "empty-everything" ]; then
    # 2. Un-normalised CRLF hazard breaks derivation
    crlf_raw=$(printf '%s\n' "$bash_raw" | sed 's/$/\r/')
    crlf_derived=$(printf '%s\n' "$crlf_raw" | bash "$DERIVE")
    if [ "$crlf_derived" != "$bash_derived" ]; then
      printf '  %-34s %-24s %s\n' "$name" "un-normalised CRLF differs" "ok (hazard real)"
    else
      printf '  %-34s %-24s %s\n' "$name" "un-normalised CRLF differs" "FAIL (hazard silent)"
      fail=1
    fi

    # 3. Un-normalised leading whitespace hazard breaks derivation
    ws_raw=$(printf '%s\n' "$bash_raw" | sed 's/^/  /')
    ws_derived=$(printf '%s\n' "$ws_raw" | bash "$DERIVE")
    if [ "$ws_derived" != "$bash_derived" ]; then
      printf '  %-34s %-24s %s\n' "$name" "leading whitespace differs" "ok (hazard real)"
    else
      printf '  %-34s %-24s %s\n' "$name" "leading whitespace differs" "FAIL (hazard silent)"
      fail=1
    fi

    # 4. Bare values without keys produce empty/different derivation
    bare_raw=$(printf '%s\n' "$bash_raw" | cut -d= -f2-)
    bare_derived=$(printf '%s\n' "$bare_raw" | bash "$DERIVE")
    if [ "$bare_derived" != "$bash_derived" ]; then
      printf '  %-34s %-24s %s\n' "$name" "bare values differ" "ok (hazard real)"
    else
      printf '  %-34s %-24s %s\n' "$name" "bare values differ" "FAIL (hazard silent)"
      fail=1
    fi
  fi
done

echo
if [ "$fail" -ne 0 ]; then
  echo "  Hazard verification or raw agreement failed."
  exit 1
fi
echo "  Raw agreement and un-normalised hazard checks passed."
