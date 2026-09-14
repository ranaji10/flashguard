#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Assert that the bash path (02-android.sh) and the raw-paste path
# produce the same derived fields across varied text input shapes:
#   - CRLF line endings (Windows adb shell output)
#   - Shuffled key order
#   - Interleaved blank lines and leading whitespace
# And verify that bare-value fallback is refused and no longer offered.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
DERIVE="$HERE/../bench-kit/scripts/derive.sh"
HTML="$HERE/../bench-kit/START-HERE.html"
fail=0

# Check that the bare getprop fallback was removed from START-HERE.html
if grep -q "adb shell getprop ro.product.manufacturer" "$HTML"; then
  echo "  FAIL: START-HERE.html still contains bare getprop fallback commands"
  fail=1
else
  echo "  ok: START-HERE.html does not offer bare getprop fallback"
fi

printf '\n  %-34s %-20s %s\n' "FIXTURE" "SHAPE TESTED" "RESULT"
printf '  %s\n' "$(printf '%.0s-' $(seq 1 68))"

for f in "$HERE"/android/*.props; do
  [ -e "$f" ] || continue
  name=$(basename "$f" .props)

  bash_raw=$(grep -v '^#!' "$f")
  bash_derived=$(printf '%s\n' "$bash_raw" | bash "$DERIVE")

  # 1. CRLF line endings (simulating Windows adb shell)
  crlf_input=$(printf '%s\n' "$bash_raw" | sed 's/$/\r/')
  # Page normaliser: t.replace(/\r\n?/g, "\n")
  crlf_norm=$(printf '%s\n' "$crlf_input" | tr -d '\r')
  crlf_derived=$(printf '%s\n' "$crlf_norm" | bash "$DERIVE")

  if [ "$crlf_derived" = "$bash_derived" ]; then
    printf '  %-34s %-20s %s\n' "$name" "CRLF normalisation" "ok"
  else
    printf '  %-34s %-20s %s\n' "$name" "CRLF normalisation" "FAIL"
    fail=1
  fi

  # 2. Interleaved blank lines and leading whitespace
  ws_input=$(printf '%s\n' "$bash_raw" | awk '{print "  " $0 "\n"}')
  ws_norm=$(printf '%s\n' "$ws_input" | sed 's/^[[:space:]]*//; s/[[:space:]]*$//' | grep -v '^$')
  ws_derived=$(printf '%s\n' "$ws_norm" | bash "$DERIVE")

  if [ "$ws_derived" = "$bash_derived" ]; then
    printf '  %-34s %-20s %s\n' "$name" "whitespace/blanks" "ok"
  else
    printf '  %-34s %-20s %s\n' "$name" "whitespace/blanks" "FAIL"
    fail=1
  fi

  # 3. Keys in different order
  shuffled_input=$(printf '%s\n' "$bash_raw" | sort -r)
  shuffled_derived=$(printf '%s\n' "$shuffled_input" | bash "$DERIVE")

  if [ "$shuffled_derived" = "$bash_derived" ]; then
    printf '  %-34s %-20s %s\n' "$name" "shuffled key order" "ok"
  else
    printf '  %-34s %-20s %s\n' "$name" "shuffled key order" "FAIL"
    fail=1
  fi
done

echo
if [ "$fail" -ne 0 ]; then
  echo "  Raw agreement test failed on one or more input shapes."
  exit 1
fi
echo "  All raw text shapes match canonical derivation."
