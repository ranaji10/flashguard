#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Tier A fastboot view. READ-ONLY.
#
# Queries named variables one at a time. It deliberately does NOT run
# `fastboot getvar all` or `fastboot devices`, both of which print the
# device serial number.
#
# Nothing here writes. See STOP-LIST.txt for what must never be run.
set -u

echo
echo "=== fastboot (read-only) ==================================="
echo
echo "  This reboots the phone into its bootloader, reads a few variables,"
echo "  and reboots it back. A reboot is not a write."
echo
read -r -p "  Phone charged above 50%? [y/N] " ok
case "$ok" in y|Y) ;; *) echo "  Charge it first. Nothing lost by waiting."; exit 0 ;; esac

STATE=$(adb get-state 2>/dev/null || true)
if [ "$STATE" = "device" ]; then
  echo
  echo "  rebooting into bootloader..."
  adb reboot bootloader
  sleep 6
else
  echo
  echo "  No adb device. Put the phone in bootloader mode manually if you know how,"
  echo "  otherwise stop here."
fi

VARS="product variant unlocked secure current-slot slot-count is-userspace hw-revision"

echo
for v in $VARS; do
  out=$(fastboot getvar "$v" 2>&1 | head -1 | tr -d '\r')
  printf '  %-16s %s\n' "$v" "${out:-<no answer>}"
done

echo
echo "  rebooting back to system..."
fastboot reboot >/dev/null 2>&1 || echo "  ! reboot command failed, reboot the phone by hand"

cat <<'TAIL'

  If a variable came back empty or unsupported, that is a finding worth a
  note. Fastboot variable support is inconsistent between vendors, which is
  itself an argument for cannot-verify as a real verdict.

TAIL
