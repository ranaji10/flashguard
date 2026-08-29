#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
#
# derive.sh -- turn raw Android properties into the fields the verifier needs.
# PURE FUNCTION. `key=value` lines on stdin, `key<TAB>value` lines on stdout.
# No device, no adb, no side effects. Same shape as classify.sh, same reason:
# 02-android.sh had never run to completion on a real device, so none of this
# reasoning had ever been exercised. Now tests/run-android.sh exercises it.
#
# The three fields the verifier actually turns on -- partition scheme, bootloader
# state, chipset family -- are derived here and NOWHERE else.
set -u
declare -A P=()
while IFS= read -r line; do
  case "$line" in ''|'#'*) continue;; esac
  k="${line%%=*}"; v="${line#*=}"
  P["$k"]="$v"
done
g(){ printf '%s' "${P[$1]:-}"; }

# ---- partition scheme -------------------------------------------------------
# Abstains rather than guessing. The previous logic said "if we could read the
# Android version at all, call it single", which turns a missing property into a
# confident answer -- the exact failure mode this project exists to prevent.
AB=$(g ro.build.ab_update); SLOT=$(g ro.boot.slot_suffix); VAB=$(g ro.virtual_ab.enabled)
if   [ "$VAB" = "true" ];      then SCHEME="virtual_A/B"; SCHEME_WHY="ro.virtual_ab.enabled=true"
elif [ "$AB"  = "true" ];      then SCHEME="A/B";         SCHEME_WHY="ro.build.ab_update=true"
elif [ -n "$SLOT" ];           then SCHEME="A/B";         SCHEME_WHY="ro.boot.slot_suffix=$SLOT"
elif [ "$AB"  = "false" ];     then SCHEME="single";      SCHEME_WHY="ro.build.ab_update=false"
else SCHEME="unknown"
     SCHEME_WHY="no ab_update, no slot_suffix, no virtual_ab -- absent is not the same as single"
fi

# ---- bootloader state -------------------------------------------------------
# Four sources, most explicit first. Vendors disagree about which they expose;
# Samsung devices of the A5 era often expose none of them.
LOCK=$(g ro.boot.flash.locked); DEVST=$(g ro.boot.vbmeta.device_state); VBS=$(g ro.boot.verifiedbootstate)
case "$LOCK" in
  1) BL="locked";   BL_WHY="ro.boot.flash.locked=1" ;;
  0) BL="unlocked"; BL_WHY="ro.boot.flash.locked=0" ;;
  *) case "$DEVST" in
       locked)   BL="locked";   BL_WHY="ro.boot.vbmeta.device_state=locked" ;;
       unlocked) BL="unlocked"; BL_WHY="ro.boot.vbmeta.device_state=unlocked" ;;
       *) case "$VBS" in
            green)  BL="locked";   BL_WHY="verifiedbootstate=green" ;;
            orange) BL="unlocked"; BL_WHY="verifiedbootstate=orange" ;;
            yellow) BL="locked_custom_key"; BL_WHY="verifiedbootstate=yellow" ;;
            red)    BL="verification_failed"; BL_WHY="verifiedbootstate=red" ;;
            *) BL="unknown"; BL_WHY="no lock property exposed by this device" ;;
          esac ;;
     esac ;;
esac
[ -z "$VBS" ] && VBS="unknown"

# ---- chipset family ---------------------------------------------------------
# "Chipset families covered" is one of the numbers the grant is measured on, so
# where the value came from is recorded with it. ro.board.platform is empty on a
# lot of Samsung hardware, which would have read as zero families covered.
SOCM=$(g ro.soc.model); SOCV=$(g ro.soc.manufacturer)
PLAT=$(g ro.board.platform); HW=$(g ro.hardware); BOARD=$(g ro.product.board)
if   [ -n "$SOCM" ];  then CHIP="${SOCV:+$SOCV }$SOCM"; CHIP_SRC="ro.soc.model"
elif [ -n "$PLAT" ];  then CHIP="$PLAT";  CHIP_SRC="ro.board.platform"
elif [ -n "$HW" ];    then CHIP="$HW";    CHIP_SRC="ro.hardware"
elif [ -n "$BOARD" ]; then CHIP="$BOARD"; CHIP_SRC="ro.product.board"
else CHIP="unknown"; CHIP_SRC="none"
fi

n(){ printf '%s' "${1:-unknown}"; }
p(){ printf '%s\t%s\n' "$1" "$2"; }
p manufacturer      "$(n "$(g ro.product.manufacturer)")"
p product_model     "$(n "$(g ro.product.model)")"
p product_device    "$(n "$(g ro.product.device)")"
p product_board     "$(n "$BOARD")"
p board_platform    "$(n "$PLAT")"
p hardware          "$(n "$HW")"
p chipset_family    "$CHIP"
p chipset_source    "$CHIP_SRC"
p cpu_abi           "$(n "$(g ro.product.cpu.abi)")"
p android_version   "$(n "$(g ro.build.version.release)")"
p sdk               "$(n "$(g ro.build.version.sdk)")"
p security_patch    "$(n "$(g ro.build.version.security_patch)")"
p build_fingerprint "$(n "$(g ro.build.fingerprint)")"
p partition_scheme  "$SCHEME"
p partition_basis   "$SCHEME_WHY"
p slot_suffix       "$SLOT"
p bootloader_state  "$BL"
p bootloader_basis  "$BL_WHY"
p verified_boot_state "$VBS"
p bootloader_unlockable "unknown"
