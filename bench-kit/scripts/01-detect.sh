#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Tier A detect. Read-only. Diffs USB against the baseline, classifies what
# appeared, and emits one capture line for the browser.
#
# Classifier v2, 29 Aug 2026. v1 called every USB class-0x06 device a camera,
# which meant two real Android phones in file-transfer mode were recorded as
# ptp_camera. See raw/2026-08-29 bench run.
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
    4. on a phone, pull down the notification shade and pick a USB mode
       (File transfer / MTP). Many phones default to "charging only".
    5. on a camera, check its USB mode in the menu.

  "Not detected, and here is what I tried" IS a valid record.

NONE
  emit 'BENCH_CAPTURE {"device_class":"not_detected","usb_vendor_id":"unknown","usb_product_id":"unknown","usb_interface_class":"unknown","classifier_confidence":null,"_detected":false}'
  exit 0
fi

if [ "$COUNT" -gt 1 ]; then
  echo; echo "  MORE THAN ONE new device appeared:"
  echo "$NEW" | sed 's/^/    /'
  echo; echo "  Unplug all but one and run this again."
  exit 1
fi

ID=$(printf '%s' "$NEW" | grep -oE 'ID [0-9a-f]{4}:[0-9a-f]{4}' | head -1 | awk '{print $2}')
VID="0x${ID%%:*}"; PID="0x${ID##*:}"
DESC=$(printf '%s' "$NEW" | sed -E 's/.*ID [0-9a-f]{4}:[0-9a-f]{4} ?//')

V=$(sudo lsusb -v -d "$ID" 2>/dev/null)

# Read EVERY interface, not just the first. A phone with USB debugging on is a
# COMPOSITE device: interface 0 is MTP (class 06) and the ADB interface
# (ff/42/01) comes after it. Reading only the first missed every such phone on
# the 29 Aug run, including one that was correctly configured.
ICLASS=$(printf '%s' "$V" | grep -m1 -oE 'bInterfaceClass +[0-9]+' | awk '{printf "0x%02x", $2}')
ALLCLASS=$(printf '%s' "$V" | grep -oE 'bInterfaceClass +[0-9]+' | awk '{printf "0x%02x ", $2}' | tr -s ' ')
ISUB=$(printf   '%s' "$V" | grep -m1 -oE 'bInterfaceSubClass +[0-9]+' | awk '{print $2}')
IPROT=$(printf  '%s' "$V" | grep -m1 -oE 'bInterfaceProtocol +[0-9]+' | awk '{print $2}')

# The ADB interface triple is class 255 / subclass 66 / protocol 1, anywhere in
# the descriptor. Look for the three on consecutive lines.
HAS_ADB=$(printf '%s' "$V" | grep -A2 'bInterfaceClass *255' | grep -q 'bInterfaceProtocol *1' && echo yes || echo no)
HAS_FB=$(printf  '%s' "$V" | grep -A2 'bInterfaceClass *255' | grep -q 'bInterfaceProtocol *3' && echo yes || echo no)

# Definitive: if adb itself can see it, it is an Android with debugging on.
# get-state does not print the serial, unlike `adb devices`.
ADBSTATE=$(adb get-state 2>/dev/null || true)
IPROD=$(printf  '%s' "$V" | grep -m1 -E '^\s*iProduct' | sed -E 's/.*iProduct +[0-9]+ +//')
# iInterface strings are the MTP-vs-PTP discriminator. Collect them all.
IFACE=$(printf  '%s' "$V" | grep -E '^\s*iInterface' | sed -E 's/.*iInterface +[0-9]+ +//' | paste -sd'|' -)
[ -z "${ICLASS:-}" ] && ICLASS="unknown"

# vendors that ship phones. Class 0x06 from one of these is far more likely a
# phone in file-transfer mode than a camera.
PHONE_VENDORS="0x18d1 0x04e8 0x2717 0x22b8 0x2a70 0x05c6 0x0fce 0x12d1 0x19d2 0x1004 0x0b05 0x0489 0x2d95 0x0e8d 0x2916 0x1bbb"
CAMERA_VENDORS="0x04cb 0x04a9 0x04b0 0x04da 0x07b4 0x0471"

is_in(){ case " $2 " in *" $1 "*) return 0;; *) return 1;; esac; }

CLASS="unknown"; CONF="0.3"; HINT=""
if [ "$ADBSTATE" = "device" ]; then
  CLASS="adb"; CONF="0.99"
  HINT="adb can talk to this device. Debugging is on and authorised. Run 02-android.sh next."
elif [ "$ADBSTATE" = "unauthorized" ]; then
  CLASS="adb"; CONF="0.99"
  HINT="adb SEES this device but is not authorised. Look at the PHONE SCREEN: there is a prompt asking whether to allow debugging from this computer. Tick 'always allow' and accept, then run 01-detect.sh again."
elif [ "$HAS_ADB" = "yes" ]; then
  CLASS="adb"; CONF="0.9"
  HINT="An ADB interface is present even though adb is not connected. Try a different cable or port, and check the phone screen for an authorisation prompt."
elif [ "$HAS_FB" = "yes" ]; then
  CLASS="fastboot"; CONF="0.9"
elif [ "$VID" = "0x05ac" ]; then
  CLASS="ios"; CONF="0.95"; HINT="Apple device. Unsupported for flashing by design. Correct negative."
else
  case "$ICLASS" in
    0x08) CLASS="mass_storage"; CONF="0.95" ;;
    0x06)
      if printf '%s' "$IFACE" | grep -qi 'MTP'; then
        CLASS="mtp"; CONF="0.85"
        HINT="Interface reports MTP, not PTP. If this is a phone, it is in file-transfer mode."
      elif is_in "$VID" "$PHONE_VENDORS"; then
        CLASS="mtp"; CONF="0.5"
        HINT="USB class 0x06 from a PHONE vendor. Almost certainly a phone in file-transfer mode, NOT a camera. To fingerprint it you must enable USB debugging, see below."
      elif is_in "$VID" "$CAMERA_VENDORS"; then
        CLASS="ptp_camera"; CONF="0.8"
        HINT="USB class 0x06 from a camera vendor. Confirm PTP versus card-reader in the camera menu."
      else
        CLASS="ptp_or_mtp"; CONF="0.3"
        HINT="USB class 0x06 covers BOTH cameras (PTP) and phones (MTP), and this vendor is in neither list. You decide."
      fi ;;
    0xff)
      if [ "${ISUB:-}" = "66" ] && [ "${IPROT:-}" = "1" ]; then CLASS="adb"; CONF="0.9"
      elif [ "${ISUB:-}" = "66" ] && [ "${IPROT:-}" = "3" ]; then CLASS="fastboot"; CONF="0.9"
      fi ;;
  esac
fi
printf '%s' "$IPROD $IFACE" | grep -qi 'fastboot' && { CLASS="fastboot"; CONF="0.9"; }

echo
echo "  DETECTED"
echo "    $DESC"
printf '    %-22s %s\n' "vendor:product" "$VID:$PID"
printf '    %-22s %s\n' "interface class" "$ICLASS"
printf '    %-22s %s\n' "all interfaces" "$ALLCLASS"
printf '    %-22s %s\n' "adb sees it" "${ADBSTATE:-no}"
[ -n "${IPROD:-}" ]  && printf '    %-22s %s\n' "product string" "$IPROD"
[ -n "${IFACE:-}" ]  && printf '    %-22s %s\n' "interface strings" "$IFACE"
echo
echo "  BEST GUESS: $CLASS  (confidence $CONF)"
[ -n "$HINT" ] && echo "  $HINT"

if is_in "$VID" "$PHONE_VENDORS" && [ "$CLASS" != "adb" ] && [ "$CLASS" != "fastboot" ] && [ -z "$ADBSTATE" ]; then
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
  Then unplug, replug, accept the prompt on the phone screen, and run:
    bash 02-android.sh

  Record this capture anyway. A phone that shows up as class 0x06 with
  debugging off is a real and common condition worth having in the matrix.
PHONE
fi

emit "BENCH_CAPTURE {\"device_class\":\"$(jesc "$CLASS")\",\"usb_vendor_id\":\"$VID\",\"usb_product_id\":\"$PID\",\"usb_interface_class\":\"$(jesc "$ICLASS")\",\"classifier_confidence\":$CONF,\"_lsusb\":\"$(jesc "$DESC")\",\"_product_string\":\"$(jesc "${IPROD:-}")\",\"_iface_string\":\"$(jesc "${IFACE:-}")\",\"_all_interface_classes\":\"$(jesc "${ALLCLASS:-}")\",\"_adb_state\":\"$(jesc "${ADBSTATE:-none}")\",\"_hint\":\"$(jesc "$HINT")\",\"_detected\":true}"
