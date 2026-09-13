#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
#
# classify.sh -- the USB classifier, as a PURE FUNCTION.
#
# Reads a `lsusb -v` descriptor on stdin. Writes tab-separated key/value lines
# on stdout. Touches no device, needs no device, and has no side effects.
#
# It is a separate file from 01-detect.sh for one reason: a classifier that can
# only be exercised by plugging in a phone can only be debugged by plugging in a
# phone. Both classifier bugs found on 29 Aug 2026 were sitting in data already
# collected. Split this way, every saved descriptor becomes a test case and
# `tests/run.sh` replays all of them in under a second.
#
# The same shape the verifier itself must have:
#   verify(fingerprint, recipe) -> verdict, no device I/O.
#
# Optional header lines may precede the descriptor. They carry the facts that
# are true of the moment of capture rather than of the descriptor:
#   #!adb_state=device|unauthorized|offline|none
#   #!expect=<class>        (read by tests/run.sh, ignored here)
#   #!note=<free text>
# ADB_STATE in the environment overrides the header.

set -u

IN=$(cat)
HDR=$(printf '%s\n' "$IN" | sed -n 's/^#!//p')
BODY=$(printf '%s\n' "$IN" | grep -v '^#!' || true)

hdr(){ printf '%s\n' "$HDR" | sed -n "s/^$1=//p" | head -1; }

ADBSTATE="${ADB_STATE:-$(hdr adb_state)}"
[ -z "$ADBSTATE" ] && ADBSTATE="none"

VID=$(printf '%s\n' "$BODY" | grep -m1 -oE 'idVendor +0x[0-9a-f]{4}'  | grep -oE '0x[0-9a-f]{4}')
PID=$(printf '%s\n' "$BODY" | grep -m1 -oE 'idProduct +0x[0-9a-f]{4}' | grep -oE '0x[0-9a-f]{4}')
: "${VID:=unknown}" "${PID:=unknown}"

# Walk the interface descriptors properly. lsusb -v emits class, subclass and
# protocol in that order inside each interface block, so completing a triple on
# the protocol line groups them correctly. WebUSB outputs interface lines with
# class, subclass and protocol inline.
TRIPLES=$(printf '%s\n' "$BODY" | awk '
  $1=="bInterfaceClass"    { c=$2; next }
  $1=="bInterfaceSubClass" { s=$2; next }
  $1=="bInterfaceProtocol" { if (c!="") print c"/"s"/"$2; c=""; s=""; next }
  /class [0-9]+ +subclass [0-9]+ +protocol [0-9]+/ {
    c=""; s=""; p=""
    for (i=1; i<=NF; i++) {
      if ($i=="class") c=$(i+1)
      if ($i=="subclass") s=$(i+1)
      if ($i=="protocol") p=$(i+1)
    }
    if (c!="" && s!="" && p!="") print c"/"s"/"p
    c=""; s=""; p=""
  }
')

ALLCLASS=$(printf '%s\n' "$TRIPLES" | awk -F/ 'NF{printf "0x%02x ", $1}' | sed 's/ $//')
ICLASS=$(printf   '%s\n' "$TRIPLES" | awk -F/ 'NR==1&&NF{printf "0x%02x", $1}')
ISUB=$(printf     '%s\n' "$TRIPLES" | awk -F/ 'NR==1&&NF{print $2}')
IPROT=$(printf    '%s\n' "$TRIPLES" | awk -F/ 'NR==1&&NF{print $3}')
[ -z "${ICLASS:-}" ] && ICLASS="unknown"

has_triple(){ printf '%s\n' "$TRIPLES" | grep -qx "$1"; }
HAS_ADB=no; has_triple "255/66/1" && HAS_ADB=yes
HAS_FB=no;  has_triple "255/66/3" && HAS_FB=yes

IPROD=$(printf '%s\n' "$BODY" | grep -m1 -E '^[[:space:]]*(iProduct|product)' | sed -E 's/.*(iProduct +[0-9]+ +|product +)//')
IFACE=$(printf '%s\n' "$BODY" | grep -E '^[[:space:]]*iInterface' | sed -E 's/.*iInterface +[0-9]+ +//' \
        | grep -v '^[[:space:]]*$' | paste -sd'|' -)

# Vendors that ship phones. USB class 0x06 from one of these is far more likely
# a phone in file-transfer mode (MTP) than a camera (PTP): the class byte is the
# same for both and cannot separate them.
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
        HINT="USB class 0x06 from a PHONE vendor. Almost certainly a phone in file-transfer mode, NOT a camera. To fingerprint it you must enable USB debugging."
      elif is_in "$VID" "$CAMERA_VENDORS"; then
        CLASS="ptp_camera"; CONF="0.8"
        HINT="USB class 0x06 from a camera vendor. Confirm PTP versus card-reader in the camera menu."
      else
        CLASS="ptp_or_mtp"; CONF="0.3"
        HINT="USB class 0x06 covers BOTH cameras (PTP) and phones (MTP), and this vendor is in neither list. You decide."
      fi ;;
    0xff)
      if   [ "${ISUB:-}" = "66" ] && [ "${IPROT:-}" = "1" ]; then CLASS="adb"; CONF="0.9"
      elif [ "${ISUB:-}" = "66" ] && [ "${IPROT:-}" = "3" ]; then CLASS="fastboot"; CONF="0.9"
      fi ;;
    # Class 0x02 with an AT-command modem interface. Added 30 Aug 2026 from a real
    # Samsung feature phone (0x04e8:0x6845) that the classifier had abstained on.
    # A CDC modem exposing AT commands is characteristic of a pre-Android handset:
    # no adb, no fastboot, and no Android recipe applies to it. Naming it is safer
    # than "unknown", which invites a human to guess. A drawer full of old phones
    # contains a lot of these.
    0x02)
      if has_triple "2/2/1"; then
        CLASS="cdc_modem"; CONF="0.85"
        HINT="Exposes an AT-command modem. Characteristic of a feature phone rather than an Android device. Out of scope for flashing: correct negative."
      else
        CLASS="cdc_other"; CONF="0.5"
        HINT="A USB communications device. Not an Android flashing target."
      fi ;;
  esac
fi
printf '%s' "${IPROD:-} ${IFACE:-}" | grep -qi 'fastboot' && { CLASS="fastboot"; CONF="0.9"; }

p(){ printf '%s\t%s\n' "$1" "$2"; }
p class            "$CLASS"
p confidence       "$CONF"
p vendor_id        "$VID"
p product_id       "$PID"
p interface_class  "$ICLASS"
p all_classes      "${ALLCLASS:-}"
p interface_triples "$(printf '%s' "$TRIPLES" | paste -sd, -)"
p has_adb          "$HAS_ADB"
p has_fastboot     "$HAS_FB"
p adb_state        "$ADBSTATE"
p product_string   "${IPROD:-}"
p interface_strings "${IFACE:-}"
p hint             "$HINT"
