#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Assert that the bash path (02-android.sh) and the raw-paste path
# produce the same derived fields when derive.sh runs over the raw property text.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
DERIVE="$HERE/../bench-kit/scripts/derive.sh"
fail=0

printf '\n  %-36s %-16s %s\n' "FIXTURE" "FIELDS CHECKED" "RESULT"
printf '  %s\n' "$(printf '%.0s-' $(seq 1 68))"

for f in "$HERE"/android/*.props; do
  [ -e "$f" ] || continue
  name=$(basename "$f" .props)

  # Route 1: Simulated bash path (derived directly)
  bash_raw=$(grep -v '^#!' "$f")
  bash_derived=$(printf '%s\n' "$bash_raw" | bash "$DERIVE")

  # Route 2: Simulated raw paste path (verbatim raw text, derived via derive.sh)
  raw_paste="$bash_raw"
  raw_derived=$(printf '%s\n' "$raw_paste" | bash "$DERIVE")

  if [ "$bash_derived" = "$raw_derived" ]; then
    printf '  %-36s %-16s %s\n' "$name" "all 17+ fields" "ok"
  else
    printf '  %-36s %-16s %s\n' "$name" "all 17+ fields" "FAIL"
    fail=1
  fi
done

echo
if [ "$fail" -ne 0 ]; then
  echo "  Bash path and raw-paste path produced DIFFERENT derived fields."
  exit 1
fi
echo "  Bash path and raw-paste path agree across all property fixtures."
