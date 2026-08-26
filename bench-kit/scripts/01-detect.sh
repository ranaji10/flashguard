#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Tier A detect. Read-only. Diffs USB against the baseline, classifies what
# appeared, and emits one capture line for the browser.
set -u
DIR="$(cd "$(dirname "$0")" && pwd)"; . "$DIR/_lib.sh"

BASE="$HOME/bench/baseline.txt"
[ -f "$BASE" ] || { echo "No baseline. Run: bash 00-setup.sh"; exit 1; }

NEW=$(diff "$BASE" <(lsusb) | sed -n 's/^> //p')
COUNT=$(printf '%s' "$NEW" | grep -c 'ID ' || true)

if [ -z "$NEW" ]; then
  cat <<'NONE'

  NOTHING NEW DETECTED.

  Before concluding the device is invisible, try in this order:
    1. a different cable. Charge-only cables are the most common cause.
    2. a different USB port, directly on the machine, not through a hub.
    3. unlock the phone screen, then unplug and replug.
    4. on a camera, check its USB mode in the menu.

  "Not detected, and here is what I tried" IS a valid record.
  Choose "not detected" in the browser and write what you tried.

NONE
  emit 'BENCH_CAPTURE {"device_class":"not_detected","usb_vendor_id":"unknown","usb_product_id":"unknown","usb_interface_class":"unknown","classifier_confidence":null,"_detected":false}'
  exit 0
fi

if [ "$COUNT" -gt 1 ]; then
  echo
  echo "  MORE THAN ONE new device appeared:"
  echo "$NEW" | sed 's/^/    /'
  echo
  echo "  Unplug all but one and run this again. One device at a time keeps"
  echo "  the records unambiguous."
  exit 1
fi

ID=$(printf '%s' "$NEW" | grep -oE 'ID [0-9a-f]{4}:[0-9a-f]{4}' | head -1 | awk '{print $2}')
VID="0x${ID%%:*}"; PID="0x${ID##*:}"
DESC=$(printf '%s' "$NEW" | sed -E 's/.*ID [0-9a-f]{4}:[0-9a-f]{4} ?//')

V=$(sudo lsusb -v -d "$ID" 2>/dev/null)
ICLASS=$(printf '%s' "$V" | grep -m1 -oE 'bInterfaceClass +[0-9]+' | awk '{printf "0x%02x", $2}')
ISUB=$(printf   '%s' "$V" | grep -m1 -oE 'bInterfaceSubClass +[0-9]+' | awk '{print $2}')
IPROT=$(printf  '%s' "$V" | grep -m1 -oE 'bInterfaceProtocol +[0-9]+' | awk '{print $2}')
IPROD=$(printf  '%s' "$V" | grep -m1 -E '^\s*iProduct' | sed -E 's/.*iProduct +[0-9]+ +//')
[ -z "${ICLASS:-}" ] && ICLASS="unknown"

# --- first version of the classifier. Deliberately conservative. ---
CLASS="unknown"; CONF="0.3"
case "$VID" in 0x05ac) CLASS="ios"; CONF="0.95" ;; esac
if [ "$CLASS" = "unknown" ]; then
  case "$ICLASS" in
    0x08) CLASS="mass_storage"; CONF="0.95" ;;
    0x06) CLASS="ptp_camera";   CONF="0.6"  ;;   # MTP shares this class. Human confirms.
    0xff)
      if [ "${ISUB:-}" = "66" ] && [ "${IPROT:-}" = "1" ]; then CLASS="adb"; CONF="0.9"
      elif [ "${ISUB:-}" = "66" ] && [ "${IPROT:-}" = "3" ]; then CLASS="fastboot"; CONF="0.9"
      fi ;;
  esac
fi
printf '%s' "$IPROD" | grep -qi 'fastboot' && { CLASS="fastboot"; CONF="0.9"; }

echo
echo "  DETECTED"
echo "    $DESC"
printf '    %-22s %s\n' "vendor:product" "$VID:$PID"
printf '    %-22s %s\n' "interface class" "$ICLASS"
[ -n "${IPROD:-}" ] && printf '    %-22s %s\n' "product string" "$IPROD"
echo
echo "  BEST GUESS: $CLASS  (confidence $CONF)"
[ "$CLASS" = "ptp_camera" ] && echo "  Note: class 0x06 covers both PTP and MTP. The browser will ask you."
[ "$CLASS" = "unknown" ]    && echo "  Note: no confident guess. That is itself a useful record."

emit "BENCH_CAPTURE {\"device_class\":\"$(jesc "$CLASS")\",\"usb_vendor_id\":\"$VID\",\"usb_product_id\":\"$PID\",\"usb_interface_class\":\"$(jesc "$ICLASS")\",\"classifier_confidence\":$CONF,\"_lsusb\":\"$(jesc "$DESC")\",\"_product_string\":\"$(jesc "${IPROD:-}")\",\"_detected\":true}"
