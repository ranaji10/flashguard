#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Tier A setup. Installs read-only tools and takes the USB baseline.
# Nothing here touches a connected device.
set -u

BENCH="$HOME/bench"
echo
echo "=== Tier A setup ==========================================="
echo

mkdir -p "$BENCH/raw"
echo "  working directory: $BENCH"

echo
echo "--- installing tools (needs network + sudo) ---"
sudo apt update -qq || echo "  ! apt update failed, continuing"
if ! sudo apt install -y usbutils adb fastboot 2>/dev/null; then
  echo "  package names differ on this release, trying the older ones"
  sudo apt install -y usbutils android-tools-adb android-tools-fastboot \
    || echo "  ! install failed. Check network, then re-run."
fi

echo
echo "--- versions ---"
for t in lsusb adb fastboot; do
  if command -v "$t" >/dev/null 2>&1; then
    printf '  %-10s %s\n' "$t" "$(command -v $t)"
  else
    printf '  %-10s MISSING\n' "$t"
  fi
done

echo
echo "--- baseline ---"
echo "  UNPLUG every device you are testing, leave only keyboard/mouse."
read -r -p "  Press Enter when nothing under test is connected... " _

lsusb > "$BENCH/baseline.txt"
echo
echo "  baseline devices:"
awk '{print "    " NR ") " $0}' "$BENCH/baseline.txt"
echo
printf '  Is the phone or tablet you are about to test in this list? [y/N] '
read -r ans
case "$ans" in
  [yY]|[yY][eE][sS])
    rm -f "$BENCH/baseline.txt"
    echo
    echo "  Unplug it, then run bash 00-setup.sh again"
    exit 1
    ;;
esac
echo
echo "  baseline written: $BENCH/baseline.txt"
echo "  $(wc -l < "$BENCH/baseline.txt") devices are part of the machine itself"
echo
echo "  Next: plug in ONE device and run  bash 01-detect.sh"
echo
