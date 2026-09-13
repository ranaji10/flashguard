#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Assert that classify.sh produces the same classification from WebUSB-captured
# descriptors as from lsusb -v captures for the same physical devices.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
CLASSIFY="$HERE/../bench-kit/scripts/classify.sh"
fail=0

pairs="
18d1-4ee2:18d1-4ee2-20260830-001344.desc:adb
04e8-6860:04e8-6860-20260830-000701.desc:adb
05ac-12a8:05ac-12a8-20260830-000206.desc:ios
"

printf '\n  %-32s %-12s %-12s %-12s %s\n' "WEBUSB FIXTURE" "EXPECTED" "LSUSB" "WEBUSB" ""
printf '  %s\n' "$(printf '%.0s-' $(seq 1 76))"

for item in $pairs; do
  [ -z "$item" ] && continue
  id=$(printf '%s' "$item" | cut -d: -f1)
  lsusb_file=$(printf '%s' "$item" | cut -d: -f2)
  expect=$(printf '%s' "$item" | cut -d: -f3)

  webusb_path="$HERE/webusb-fixtures/$id.desc"
  lsusb_path="$HERE/real-descriptors/$lsusb_file"

  if [ ! -f "$webusb_path" ]; then
    echo "  MISSING WebUSB fixture: $webusb_path"
    fail=1
    continue
  fi
  if [ ! -f "$lsusb_path" ]; then
    echo "  MISSING lsusb descriptor: $lsusb_path"
    fail=1
    continue
  fi

  got_lsusb=$(ADB_STATE="" bash "$CLASSIFY" < "$lsusb_path" | awk -F'\t' '$1=="class"{print $2}')
  got_webusb=$(ADB_STATE="" bash "$CLASSIFY" < "$webusb_path" | awk -F'\t' '$1=="class"{print $2}')

  if [ "$got_webusb" = "$expect" ] && [ "$got_webusb" = "$got_lsusb" ]; then
    printf '  %-32s %-12s %-12s %-12s %s\n' "$id" "$expect" "$got_lsusb" "$got_webusb" "ok"
  else
    printf '  %-32s %-12s %-12s %-12s %s\n' "$id" "$expect" "$got_lsusb" "$got_webusb" "FAIL"
    fail=1
  fi
done

echo
if [ "$fail" -ne 0 ]; then
  echo "  WebUSB and lsusb routes disagree or failed to classify."
  exit 1
fi
echo "  WebUSB and lsusb routes agree across all fixtures."
