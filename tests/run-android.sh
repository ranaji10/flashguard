#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Replay saved Android property sets through derive.sh and check the three
# fields the verifier turns on: partition scheme, bootloader state, and where
# the chipset value came from. No device needed.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
D="$HERE/../bench-kit/scripts/derive.sh"
pass=0; fail=0
printf '\n  %-34s %-14s %-14s %s\n' FIXTURE FIELD EXPECTED "GOT"
printf '  %s\n' "$(printf '%.0s-' $(seq 1 84))"
for f in "$HERE"/android/*.props; do
  [ -e "$f" ] || continue
  name=$(basename "$f" .props)
  out=$(grep -v '^#!' "$f" | bash "$D")
  gv(){ printf '%s\n' "$out" | awk -F'\t' -v k="$1" '$1==k{print $2}'; }
  first=1
  for pair in scheme:partition_scheme bootloader:bootloader_state chipset_source:chipset_source; do
    hk="${pair%%:*}"; ok="${pair##*:}"
    want=$(sed -n "s/^#!expect_$hk=//p" "$f" | head -1); [ -z "$want" ] && continue
    got=$(gv "$ok")
    label=$([ $first = 1 ] && echo "$name" || echo ""); first=0
    if [ "$got" = "$want" ]; then
      printf '  %-34s %-14s %-14s %s\n' "$label" "$hk" "$want" "$got ok"; pass=$((pass+1))
    else
      printf '  %-34s %-14s %-14s %s\n' "$label" "$hk" "$want" "$got FAIL"; fail=$((fail+1))
    fi
  done
done
echo; echo "  $pass passed, $fail failed"; echo
[ "$fail" -gt 0 ] && exit 1 || exit 0
