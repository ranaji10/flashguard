#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Tier A Android fingerprint. READ-ONLY.
#
# Queries an EXPLICIT ALLOWLIST of properties, one at a time. It does NOT run
# bare `adb shell getprop` and does NOT run `adb devices`, because both print the
# device serial and this dataset is published. Do not turn this into a dump.
set -u
DIR="$(cd "$(dirname "$0")" && pwd)"; . "$DIR/_lib.sh"

STATE=$(adb get-state 2>/dev/null || true)
case "$STATE" in
  device) echo; echo "  adb: connected and authorised" ;;
  unauthorized)
    cat <<'UA'

  NOT AUTHORISED YET.
  Look at the phone screen. There is a prompt asking whether to allow USB
  debugging from this computer. Tick "always allow", press Allow, then run
  this script again.

UA
    exit 1 ;;
  *)
    cat <<'NOD'

  NO PHONE IN ADB MODE.

  On the phone:
    Settings > About phone > tap "Build number" seven times
    Settings > System > Developer options > USB debugging  ON
  Then unplug, replug, and run this again.

NOD
    exit 1 ;;
esac

get() { adb shell getprop "$1" 2>/dev/null | tr -d '\r\n'; }

MANU=$(get ro.product.manufacturer);  MODEL=$(get ro.product.model)
DEV=$(get ro.product.device);         BOARD=$(get ro.product.board)
PLAT=$(get ro.board.platform);        HW=$(get ro.hardware)
REL=$(get ro.build.version.release);  SDK=$(get ro.build.version.sdk)
PATCH=$(get ro.build.version.security_patch)
FP=$(get ro.build.fingerprint);       ABU=$(get ro.build.ab_update)
SLOT=$(get ro.boot.slot_suffix);      VBS=$(get ro.boot.verifiedbootstate)
LOCK=$(get ro.boot.flash.locked)

echo
echo "  FINGERPRINT (allowlisted properties only)"
printf '    %-22s %s\n' "manufacturer" "${MANU:-<empty>}"
printf '    %-22s %s\n' "model"        "${MODEL:-<empty>}"
printf '    %-22s %s\n' "codename"     "${DEV:-<empty>}"
printf '    %-22s %s\n' "chipset"      "${PLAT:-<empty>}"
printf '    %-22s %s\n' "android"      "${REL:-<empty>} (sdk ${SDK:-?})"
printf '    %-22s %s\n' "security patch" "${PATCH:-<empty>}"

if [ -n "$SLOT" ]; then SCHEME="A/B"
elif [ -n "$ABU" ] || [ -n "$REL" ]; then SCHEME="single"
else SCHEME="unknown"; fi

case "$LOCK" in 1) BL="locked" ;; 0) BL="unlocked" ;; *) BL="unknown" ;; esac
[ -z "$VBS" ] && VBS="unknown"

echo
echo "  WHAT THAT MEANS"
printf '    %-22s %s\n' "partition scheme" "$SCHEME"
printf '    %-22s %s\n' "bootloader"       "$BL"
printf '    %-22s %s\n' "verified boot"    "$VBS"
printf '    %-22s %s\n' "unlockable"       "unknown  <- correct answer, not a gap"
cat <<'TAIL'

    Whether a bootloader CAN be unlocked is generally not determinable
    read-only. Recording "unknown" honestly is the point. Guessing here is
    how a verifier learns to be wrong.
TAIL

emit "BENCH_CAPTURE {\"device_class\":\"adb\",\"android\":{\"manufacturer\":\"$(jesc "${MANU:-unknown}")\",\"product_model\":\"$(jesc "${MODEL:-unknown}")\",\"product_device\":\"$(jesc "${DEV:-unknown}")\",\"product_board\":\"$(jesc "${BOARD:-unknown}")\",\"board_platform\":\"$(jesc "${PLAT:-unknown}")\",\"hardware\":\"$(jesc "${HW:-unknown}")\",\"android_version\":\"$(jesc "${REL:-unknown}")\",\"sdk\":\"$(jesc "${SDK:-unknown}")\",\"security_patch\":\"$(jesc "${PATCH:-unknown}")\",\"build_fingerprint\":\"$(jesc "${FP:-unknown}")\",\"partition_scheme\":\"$SCHEME\",\"slot_suffix\":\"$(jesc "${SLOT:-}")\",\"bootloader_state\":\"$BL\",\"verified_boot_state\":\"$(jesc "$VBS")\",\"bootloader_unlockable\":\"unknown\"},\"_detected\":true}"
