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
#
# PORTABILITY: bash 3.2 compatible. macOS still ships bash 3.2, so no
# associative arrays (declare -A), no mapfile, no ${var,,}. tests/check-portability.sh
# enforces this. The first version of this file used declare -A, passed on Linux,
# and died on the authoring Mac -- caught by the fixtures, not by `bash -n`.
set -u
PROPS_IN=$(cat)

# Exact-prefix lookup. Property names contain dots, which are regex metacharacters,
# so this compares strings rather than matching a pattern.
g(){ printf '%s\n' "$PROPS_IN" | awk -v k="$1" 'index($0, k "=")==1 { print substr($0, length(k)+2); exit }'; }

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

# Some vendors return a legacy family label here that does not identify the chip.
# The real Samsung A5 captured on 29 Aug reported ro.board.platform=exynos5 while
# ro.hardware said samsungexynos7580 -- and the 7580 is not an Exynos 5 series part
# at all, so preferring board.platform would have filed a wrong chipset as fact.
# On a Pixel the reverse holds: board.platform=sdm670 is right and ro.hardware is
# the device codename. Neither order is universally correct, so the generic values
# are named and skipped, and every candidate is kept on the record.
case "$PLAT" in
  exynos5|exynos4|exynos3|generic|unknown|"") PLAT_USABLE="" ;;
  *) PLAT_USABLE="$PLAT" ;;
esac

if   [ -n "$SOCM" ];        then CHIP="${SOCV:+$SOCV }$SOCM"; CHIP_SRC="ro.soc.model"
elif [ -n "$PLAT_USABLE" ]; then CHIP="$PLAT_USABLE"; CHIP_SRC="ro.board.platform"
elif [ -n "$HW" ];          then CHIP="$HW";    CHIP_SRC="ro.hardware"
elif [ -n "$PLAT" ];        then CHIP="$PLAT";  CHIP_SRC="ro.board.platform_generic"
elif [ -n "$BOARD" ];       then CHIP="$BOARD"; CHIP_SRC="ro.product.board"
else CHIP="unknown"; CHIP_SRC="none"
fi
# Everything that could have answered, kept verbatim, so the choice can be redone
# later against more devices without recapturing anyone's drawer.
CHIP_CAND="soc=${SOCM:-} platform=${PLAT:-} hardware=${HW:-} board=${BOARD:-}"

# ---- firmware origin --------------------------------------------------------
# Added 8 Oct 2026 when custom-ROM handling came into scope. A ROM rewrites
# ro.product.* (Ubuntu Touch reports "Generic Device"), so identity read from those
# properties is only as good as the firmware that wrote them. Three outcomes:
#   custom   positive evidence that the running system is not the vendor's build
#   stock    user build, release-keys, and no custom marker anywhere
#   unknown  neither. A stock KaiOS phone signed with dev-keys lands here, honestly.
# Unlocked is not custom: a stock phone with an unlocked bootloader is still stock.
FP=$(g ro.build.fingerprint); REL=$(g ro.build.version.release)
FP_REL=""; FP_TYPE=""; FP_TAGS=""
case "$FP" in
  */*:*/*:*/*)
    FP_REL=${FP#*:}; FP_REL=${FP_REL%%/*}
    FP_TT=${FP##*:}; FP_TYPE=${FP_TT%%/*}; FP_TAGS=${FP_TT#*/} ;;
esac
BTYPE=$(g ro.build.type); BTAGS=$(g ro.build.tags)
[ -z "$BTYPE" ] && BTYPE="$FP_TYPE"
[ -z "$BTAGS" ] && BTAGS="$FP_TAGS"
LDEV=$(g ro.lineage.device); MANUF=$(g ro.product.manufacturer)
FW_WHY=""
if   [ -n "$LDEV" ];                     then FW_WHY="ro.lineage.device=$LDEV"
elif [ "$MANUF" = "halium" ];            then FW_WHY="ro.product.manufacturer=halium"
else case "$FP" in
       halium/*)                           FW_WHY="fingerprint brand halium" ;;
       */lineage_*|*/aosp_*)               FW_WHY="fingerprint product is a lineage_ or aosp_ build" ;;
     esac
fi
if [ -z "$FW_WHY" ]; then
  case "$BTYPE" in userdebug|eng) FW_WHY="build type $BTYPE" ;; esac
fi
if [ -z "$FW_WHY" ]; then
  case "$BTAGS" in *test-keys*) FW_WHY="build tags $BTAGS" ;; esac
fi
if [ -z "$FW_WHY" ] && [ -n "$FP_REL" ] && [ -n "$REL" ] && [ "$FP_REL" != "$REL" ]; then
  FW_WHY="fingerprint says Android $FP_REL, system says $REL"
fi
if [ -n "$FW_WHY" ]; then FW="custom"
elif [ "$BTYPE" = "user" ] && [ "$BTAGS" = "release-keys" ]; then FW="stock"; FW_WHY="user build, release-keys, no custom marker"
else FW="unknown"; FW_WHY="build ${BTYPE:-?}/${BTAGS:-?}: neither a stock nor a custom marker"
fi

# ---- launch era --------------------------------------------------------------
# The 4 Oct data split cleanly at Android 8 on the RUNNING firmware. Whether it is the
# running firmware or the launch firmware that matters is the open question, and
# first_api_level is the property that tells the two apart.
FAPI=$(g ro.product.first_api_level); FAPI_SRC="ro.product.first_api_level"
if [ -z "$FAPI" ]; then FAPI=$(g ro.board.first_api_level); FAPI_SRC="ro.board.first_api_level"; fi
[ -z "$FAPI" ] && FAPI_SRC="none"

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
p chipset_candidates "$CHIP_CAND"
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
p firmware_origin   "$FW"
p firmware_basis    "$FW_WHY"
p build_type        "$(n "$BTYPE")"
p build_tags        "$(n "$BTAGS")"
p first_api_level   "$(n "$FAPI")"
p first_api_source  "$FAPI_SRC"
p treble_enabled    "$(n "$(g ro.treble.enabled)")"
p dynamic_partitions "$(n "$(g ro.boot.dynamic_partitions)")"
p build_product     "$(n "$(g ro.build.product)")"
p product_name      "$(n "$(g ro.product.name)")"
p vendor_device     "$(n "$(g ro.product.vendor.device)")"
p vendor_model      "$(n "$(g ro.product.vendor.model)")"
p hardware_sku      "$(n "$(g ro.boot.hardware.sku)")"
p lineage_device    "$(n "$LDEV")"
