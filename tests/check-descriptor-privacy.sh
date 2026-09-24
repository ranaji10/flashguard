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
# EVERY directory holding captured descriptors, not just the one this check was written
# for. webusb-fixtures/ was added on 13 September and was outside this check on the day a
# serial was found in it -- by a reviewer reading a diff, not by this script. A privacy
# check with a directory blind spot reports clean about the place it happens to look.
DIRS=""
if [ $# -ge 1 ]; then
  if [ -d "$1" ]; then
    DIRS="$1"
  else
    echo "  directory not found: $1"
    exit 1
  fi
else
  for d in "$HERE/real-descriptors" "$HERE/webusb-fixtures" "$HERE/../bench-kit/descriptors"; do
    [ -d "$d" ] && DIRS="$DIRS $d"
  done
fi
[ -n "$DIRS" ] || { echo "  no captured descriptors yet"; exit 0; }
D="$DIRS"
fail=0

hits=$(grep -rn '^[[:space:]]*iSerial' $D 2>/dev/null || true)
if [ -n "$hits" ]; then
  echo "  iSERIAL PRESENT -- do not publish these:"; printf '%s\n' "$hits" | sed 's/^/      /'; fail=1
fi

# A SERIAL ANYWHERE, not only on the line named after it.
#
# This check reported "no serial found" on every run for two weeks while
# 18d1-4ee2-20260830-001344.desc carried YUPIK-QRD _SN:<the serial> in its iProduct string.
# 01-detect.sh strips iSerial at capture and the manufacturer had put the serial somewhere
# else. The file's own header line says "iSerial stripped" four lines above it.
#
# A check that only looks where it expects the problem reports clean and means nothing. It
# was found by a blind reviewer reading a diff, not by this script.
# Filter each MATCH, not each line: a masked serial on the same line as a raw one must not
# hide the raw one (batch 7.6 residue, fixed 24 September 2026).
hits=$(grep -rnoiE '_?SN[:=][[:space:]]*(<[^>]*>|[^[:space:]]+)' $D 2>/dev/null | grep -viE ':_?SN[:=][[:space:]]*(<stripped>|<the serial>)$' || true)
if [ -n "$hits" ]; then
  echo "  SERIAL EMBEDDED IN A STRING DESCRIPTOR -- do not publish these:"
  printf '%s\n' "$hits" | sed 's/^/      /'
  echo "      Manufacturers put the serial in iProduct or iManufacturer. Stripping iSerial"
  echo "      is not enough, and the capture note claiming it was stripped is not evidence."
  fail=1
fi
hits=$(grep -rnE '(^|[^0-9])[0-9]{15}([^0-9]|$)' $D 2>/dev/null || true)
if [ -n "$hits" ]; then
  echo "  15-digit number (IMEI shape):"; printf '%s\n' "$hits" | sed 's/^/      /'; fail=1
fi
hits=$(grep -rniE '\b([0-9a-f]{2}:){5}[0-9a-f]{2}\b' $D 2>/dev/null || true)
if [ -n "$hits" ]; then
  echo "  MAC address shape:"; printf '%s\n' "$hits" | sed 's/^/      /'; fail=1
fi

n=$(ls -1 $D/*.desc 2>/dev/null | wc -l | tr -d ' ')
[ "$fail" = 0 ] && echo "  $n descriptor(s), no serial, IMEI or MAC found"
exit "$fail"
