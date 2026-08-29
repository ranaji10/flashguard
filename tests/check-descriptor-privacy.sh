#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Descriptors are published. `lsusb -v` prints iSerial, and on many devices that
# IS the hardware serial number. 01-detect.sh strips it at capture, but a
# descriptor can also arrive from a tester who ran an older kit, or by hand, or
# through a path nobody thought about. This is the check before publication --
# not a substitute for stripping at source, a second lock on the same door.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
D="$HERE/real-descriptors"
[ -d "$D" ] || { echo "  no real-descriptors/ yet"; exit 0; }
fail=0

hits=$(grep -rn '^[[:space:]]*iSerial' "$D" 2>/dev/null || true)
if [ -n "$hits" ]; then
  echo "  iSERIAL PRESENT -- do not publish these:"; printf '%s\n' "$hits" | sed 's/^/      /'; fail=1
fi
hits=$(grep -rnE '(^|[^0-9])[0-9]{15}([^0-9]|$)' "$D" 2>/dev/null || true)
if [ -n "$hits" ]; then
  echo "  15-digit number (IMEI shape):"; printf '%s\n' "$hits" | sed 's/^/      /'; fail=1
fi
hits=$(grep -rniE '\b([0-9a-f]{2}:){5}[0-9a-f]{2}\b' "$D" 2>/dev/null || true)
if [ -n "$hits" ]; then
  echo "  MAC address shape:"; printf '%s\n' "$hits" | sed 's/^/      /'; fail=1
fi

n=$(ls -1 "$D"/*.desc 2>/dev/null | wc -l | tr -d ' ')
[ "$fail" = 0 ] && echo "  $n descriptor(s), no serial, IMEI or MAC found"
exit "$fail"
