#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Tier A detect. Read-only. Diffs USB against the baseline, hands the descriptor
# to classify.sh, and emits one capture line for the console.
#
# v4, 29 Aug 2026. The classification logic itself now lives in classify.sh as a
# pure function over descriptor text, so it can be tested without a device --
# see tests/run.sh. This file does device I/O and printing; it decides nothing.
#
# Every descriptor is also saved to descriptors/ with iSerial stripped, so each
# capture becomes a regression fixture. Both classifier bugs found on the first
# bench run were already sitting in data that had been collected and discarded.
set -u
DIR="$(cd "$(dirname "$0")" && pwd)"; . "$DIR/_lib.sh"

BASE="$HOME/bench/baseline.txt"
[ -f "$BASE" ] || { echo "No baseline. Run: bash 00-setup.sh"; exit 1; }

NEW=$(diff "$BASE" <(lsusb) | sed -n 's/^> //p')
COUNT=$(printf '%s' "$NEW" | grep -c 'ID ' || true)

if [ -z "$NEW" ]; then
  cat <<'NONE'

  NOTHING NEW DETECTED.

  Nothing new since setup. If the device was plugged in when you ran
  setup, it is in the baseline: unplug it, run bash 00-setup.sh, plug it back in, run this
  again.

  Before concluding the device is invisible, try in this order:
    1. a different cable. Charge-only cables are the most common cause.
    2. a different USB port, directly on the machine, not through a hub.
    3. unlock the phone screen, then unplug and replug.
    4. on a phone, pull down the notification shade and pick a USB mode
       (File transfer / MTP). Many phones default to "charging only".
    5. on a camera, check its USB mode in the menu.

  "Not detected, and here is what I tried" IS a valid record.

NONE
  emit 'BENCH_CAPTURE {"device_class":"not_detected","usb_vendor_id":"unknown","usb_product_id":"unknown","usb_interface_class":"unknown","classifier_confidence":null,"_detected":false}'
  exit 0
fi

if [ "$COUNT" -gt 1 ]; then
  echo
  echo "  More than one new device appeared:"
  echo "$NEW" | awk '{print "    " NR ") " $0}'
  echo
  while true; do
    printf '  Which one is the device you are testing? (1-%d): ' "$COUNT"
    read -r choice
    if [ "$choice" -ge 1 ] 2>/dev/null && [ "$choice" -le "$COUNT" ] 2>/dev/null; then
      NEW=$(printf '%s\n' "$NEW" | sed -n "${choice}p")
      break
    else
      echo "  Please enter a number between 1 and $COUNT."
    fi
  done
fi

ID=$(printf '%s' "$NEW" | grep -oE 'ID [0-9a-f]{4}:[0-9a-f]{4}' | head -1 | awk '{print $2}')
DESC=$(printf '%s' "$NEW" | sed -E 's/.*ID [0-9a-f]{4}:[0-9a-f]{4} ?//')

# iSerial is stripped here and never leaves this line. lsusb -v prints it; the
# matrix must never contain it. See data/schema.md.
#
# Try WITHOUT sudo first. Most interface descriptors are readable unprivileged,
# and a password prompt in the middle of a capture is a real place for a
# volunteer to give up -- one appeared on the 29 Aug re-run. Only escalate if the
# unprivileged read came back without any interface descriptors.
# Dropping the iSerial LINE is not enough. Manufacturers put the serial inside iProduct:
# the Nothing Phone 1 reports "YUPIK-QRD _SN:<serial>", which survived this filter, reached
# a published fixture, and sat in the repository for two weeks.
V=$(lsusb -v -d "$ID" 2>/dev/null | grep -v 'iSerial' | sed -E 's/(_?SN[:=])[[:space:]]*[A-Za-z0-9-]+/\1<stripped>/Ig')
if ! printf '%s' "$V" | grep -q 'bInterfaceClass'; then
  echo
  echo "  Reading the full descriptor needs administrator rights on this machine."
  echo "  You may be asked for your password. Nothing is written to any device;"
  echo "  this only reads how the device describes itself over USB."
  V=$(sudo lsusb -v -d "$ID" 2>/dev/null | grep -v 'iSerial' | sed -E 's/(_?SN[:=])[[:space:]]*[A-Za-z0-9-]+/\1<stripped>/Ig')
  PRIV="sudo"
else
  PRIV="user"
fi
ADBSTATE=$(adb get-state 2>/dev/null || true)

OUT=$(ADB_STATE="${ADBSTATE:-none}" bash "$DIR/classify.sh" <<< "$V")
g(){ printf '%s\n' "$OUT" | awk -F'\t' -v k="$1" '$1==k{print $2}'; }

CLASS=$(g class);            CONF=$(g confidence)
VID=$(g vendor_id);          PID=$(g product_id)
ICLASS=$(g interface_class); ALLCLASS=$(g all_classes)
TRIPLES=$(g interface_triples)
IPROD=$(g product_string);   IFACE=$(g interface_strings)
HINT=$(g hint)

# Save the descriptor as a test fixture. Prefer the kit folder so it travels back
# with the records; fall back to home if the stick is mounted read-only.
FIXDIR="$DIR/../descriptors"; mkdir -p "$FIXDIR" 2>/dev/null || FIXDIR="$HOME/bench/descriptors"
mkdir -p "$FIXDIR" 2>/dev/null || true
STAMP=$(date +%Y%m%d-%H%M%S)
FIXNAME="${VID#0x}-${PID#0x}-$STAMP.desc"
{
  echo "#!expect=$CLASS"
  echo "#!adb_state=${ADBSTATE:-none}"
  echo "#!captured=$STAMP"
  echo "#!read_privilege=${PRIV:-user}"
  echo "#!note=Captured on a real device. iSerial dropped and embedded SN masked. EDIT #!expect to the"
  echo "#!note=class a human knows this device to be, then it is a real test case."
  printf '%s\n' "$V"
} > "$FIXDIR/$FIXNAME" 2>/dev/null && SAVED="$FIXNAME" || SAVED=""

echo
echo "  DETECTED"
echo "    $DESC"
printf '    %-22s %s\n' "vendor:product"    "$VID:$PID"
printf '    %-22s %s\n' "interface class"   "$ICLASS"
printf '    %-22s %s\n' "all interfaces"    "$ALLCLASS"
printf '    %-22s %s\n' "class/sub/proto"   "$TRIPLES"
printf '    %-22s %s\n' "adb sees it"       "${ADBSTATE:-no}"
[ -n "${IPROD:-}" ] && printf '    %-22s %s\n' "product string"    "$IPROD"
[ -n "${IFACE:-}" ] && printf '    %-22s %s\n' "interface strings" "$IFACE"
[ -n "$SAVED" ]     && printf '    %-22s %s\n' "descriptor saved"  "descriptors/$SAVED"
echo
echo "  BEST GUESS: $CLASS  (confidence $CONF)"
[ -n "$HINT" ] && echo "  $HINT"

PHONE_VENDORS="0x18d1 0x04e8 0x2717 0x22b8 0x2a70 0x05c6 0x0fce 0x12d1 0x19d2 0x1004 0x0b05 0x0489 0x2d95 0x0e8d 0x2916 0x1bbb"
case " $PHONE_VENDORS " in *" $VID "*) ISPHONE=yes;; *) ISPHONE=no;; esac

if [ "$ISPHONE" = "yes" ] && [ "$CLASS" != "adb" ] && [ "$CLASS" != "fastboot" ]; then
  cat <<'PHONE'

  ---------------------------------------------------------------
  THIS LOOKS LIKE A PHONE, AND THIS CAPTURE CANNOT FINGERPRINT IT.
  ---------------------------------------------------------------
  What you have is a record of how it presents over USB. Useful, but it is
  NOT an Android fingerprint: no model, chipset, partition scheme or
  bootloader state. Those need adb, and adb needs USB debugging.

  On the phone:
    Settings > About phone > tap "Build number" seven times
    Settings > System > Developer options > USB debugging  ON
    Unlock the screen and LEAVE IT UNLOCKED
  Then unplug, replug, accept the prompt on the phone screen, and run:
    bash 02-android.sh

  Record this capture anyway. A phone that shows up as class 0x06 with
  debugging off is a real and common condition worth having in the matrix.
PHONE
fi

emit "BENCH_CAPTURE {\"device_class\":\"$(jesc "$CLASS")\",\"usb_vendor_id\":\"$VID\",\"usb_product_id\":\"$PID\",\"usb_interface_class\":\"$(jesc "$ICLASS")\",\"classifier_confidence\":$CONF,\"_lsusb\":\"$(jesc "$DESC")\",\"_product_string\":\"$(jesc "${IPROD:-}")\",\"_iface_string\":\"$(jesc "${IFACE:-}")\",\"_all_interface_classes\":\"$(jesc "${ALLCLASS:-}")\",\"_interface_triples\":\"$(jesc "${TRIPLES:-}")\",\"_adb_state\":\"$(jesc "${ADBSTATE:-none}")\",\"_read_privilege\":\"$(jesc "${PRIV:-user}")\",\"_descriptor_file\":\"$(jesc "${SAVED:-}")\",\"_hint\":\"$(jesc "$HINT")\",\"_detected\":true}"
