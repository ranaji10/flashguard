#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Tier A Android fingerprint. READ-ONLY.
#
# Queries an EXPLICIT ALLOWLIST of properties, one at a time. It does NOT run
# bare `adb shell getprop` and does NOT run `adb devices`, because both print the
# device serial and this dataset is published. Do not turn this into a dump.
#
# v2, 29 Aug 2026. All derivation moved to derive.sh, a pure function over
# key=value text, so the reasoning can be tested without a phone -- see
# tests/run-android.sh. This script talks to the device and prints; it concludes
# nothing. The previous version inferred "single partition" whenever it could
# read the Android version, which turned an absent property into a confident
# answer on exactly the field the verifier most depends on.
set -u
DIR="$(cd "$(dirname "$0")" && pwd)"; . "$DIR/_lib.sh"

# adb present? Testers who downloaded Google's platform-tools zip are told to drop the
# platform-tools folder into scripts/, so look there before giving up. Without this
# check a missing adb fell through to "NO PHONE IN ADB MODE", which sent people to
# their phone settings for a problem on the computer (first-round feedback, 18 Sep).
if ! command -v adb >/dev/null 2>&1; then
  for cand in "$DIR/platform-tools" "$HOME/Downloads/platform-tools"; do
    if [ -x "$cand/adb" ]; then PATH="$cand:$PATH"; export PATH; break; fi
  done
fi
if ! command -v adb >/dev/null 2>&1; then
  cat <<'NOADB'

  ADB IS NOT INSTALLED ON THIS COMPUTER.

  macOS:   brew install android-platform-tools
           or download "SDK Platform-Tools for Mac" from
           https://developer.android.com/tools/releases/platform-tools
           unzip it, and move the platform-tools folder into this scripts folder.
  Ubuntu:  sudo apt install adb
           (older releases: sudo apt install android-tools-adb)

  Then run this script again.

NOADB
  exit 1
fi

STATE=$(adb get-state 2>/dev/null || true)
case "$STATE" in
  device) echo; echo "  adb: connected and authorised" ;;
  unauthorized)
    cat <<'UA'

  NOT AUTHORISED YET.
  Look at the phone screen. There is a prompt asking whether to allow USB
  debugging from this computer. Tick "always allow", press Allow, then run
  this script again. If no prompt ever appears:
    Developer options > Revoke USB debugging authorisations, then replug.
  The screen must be unlocked for the prompt to show.

UA
    exit 1 ;;
  *)
    cat <<'NOD'

  NO PHONE IN ADB MODE.

  On the phone:
    Settings > About phone > tap "Build number" seven times
    Settings > System > Developer options > USB debugging  ON
    Unlock the screen and leave it unlocked
  Then unplug, replug, and run this again.

NOD
    exit 1 ;;
esac

# The allowlist. Adding a line here is a deliberate act: check it cannot carry a
# serial, an IMEI, a MAC or an account identifier before you add it.
PROPS="
ro.product.manufacturer ro.product.model ro.product.device ro.product.board
ro.board.platform ro.hardware ro.soc.manufacturer ro.soc.model ro.product.cpu.abi
ro.build.version.release ro.build.version.sdk ro.build.version.security_patch
ro.build.fingerprint ro.build.ab_update ro.virtual_ab.enabled
ro.boot.slot_suffix ro.boot.verifiedbootstate ro.boot.flash.locked
ro.boot.vbmeta.device_state
"

RAW=""
for k in $PROPS; do
  v=$(adb shell getprop "$k" 2>/dev/null | tr -d '\r\n')
  RAW="${RAW}${k}=${v}
"
done

OUT=$(printf '%s' "$RAW" | bash "$DIR/derive.sh")
g(){ printf '%s\n' "$OUT" | awk -F'\t' -v k="$1" '$1==k{print $2}'; }

echo
echo "  FINGERPRINT (allowlisted properties only)"
printf '    %-22s %s\n' "manufacturer"   "$(g manufacturer)"
printf '    %-22s %s\n' "model"          "$(g product_model)"
printf '    %-22s %s\n' "codename"       "$(g product_device)"
printf '    %-22s %s\n' "chipset"        "$(g chipset_family)"
printf '    %-22s %s\n' "chipset from"   "$(g chipset_source)"
printf '    %-22s %s\n' "cpu abi"        "$(g cpu_abi)"
printf '    %-22s %s\n' "android"        "$(g android_version) (sdk $(g sdk))"
printf '    %-22s %s\n' "security patch" "$(g security_patch)"

echo
echo "  WHAT THAT MEANS"
printf '    %-22s %-18s %s\n' "partition scheme" "$(g partition_scheme)" "$(g partition_basis)"
printf '    %-22s %-18s %s\n' "bootloader"       "$(g bootloader_state)" "$(g bootloader_basis)"
printf '    %-22s %-18s %s\n' "verified boot"    "$(g verified_boot_state)" ""
printf '    %-22s %-18s %s\n' "unlockable"       "unknown" "not determinable read-only"

UNK=0
[ "$(g partition_scheme)" = "unknown" ] && UNK=$((UNK+1))
[ "$(g bootloader_state)" = "unknown" ] && UNK=$((UNK+1))
[ "$(g chipset_source)"   = "none" ]    && UNK=$((UNK+1))
if [ "$UNK" -gt 0 ]; then
  cat <<'TAIL'

    Some fields came back unknown. That is a RESULT, not a failure, and the
    record keeps it as unknown rather than filling in a plausible value.
    Older devices -- roughly pre-2018, and Samsung hardware in particular --
    often expose no partition or bootloader property at all. A device the
    verifier cannot fingerprint read-only is precisely the case it has to
    abstain on, so these records are worth as much as the complete ones.
TAIL
fi
cat <<'TAIL2'

    Whether a bootloader CAN be unlocked is generally not determinable
    read-only. Recording "unknown" honestly is the point. Guessing here is
    how a verifier learns to be wrong.
TAIL2

j(){ jesc "$(g "$1")"; }
emit "BENCH_CAPTURE {\"device_class\":\"adb\",\"android\":{\"manufacturer\":\"$(j manufacturer)\",\"product_model\":\"$(j product_model)\",\"product_device\":\"$(j product_device)\",\"product_board\":\"$(j product_board)\",\"board_platform\":\"$(j board_platform)\",\"hardware\":\"$(j hardware)\",\"chipset_family\":\"$(j chipset_family)\",\"chipset_source\":\"$(j chipset_source)\",\"chipset_candidates\":\"$(j chipset_candidates)\",\"cpu_abi\":\"$(j cpu_abi)\",\"android_version\":\"$(j android_version)\",\"sdk\":\"$(j sdk)\",\"security_patch\":\"$(j security_patch)\",\"build_fingerprint\":\"$(j build_fingerprint)\",\"partition_scheme\":\"$(j partition_scheme)\",\"partition_basis\":\"$(j partition_basis)\",\"slot_suffix\":\"$(j slot_suffix)\",\"bootloader_state\":\"$(j bootloader_state)\",\"bootloader_basis\":\"$(j bootloader_basis)\",\"verified_boot_state\":\"$(j verified_boot_state)\",\"bootloader_unlockable\":\"unknown\"},\"_detected\":true}"
