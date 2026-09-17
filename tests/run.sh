#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Replay every saved USB descriptor through the classifier and compare the
# result with the class recorded in the fixture's `#!expect=` header.
#
# No device is needed and nothing is plugged in. Runs in about a second.
# Run it before every commit that touches classify.sh.
#
#   bash tests/run.sh            all fixtures
#   bash tests/run.sh samsung    fixtures whose name matches
#
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
CLASSIFY="$HERE/../bench-kit/scripts/classify.sh"
FILTER="${1:-}"

pass=0; fail=0; skip=0
printf '\n  %-46s %-14s %-14s %s\n' FIXTURE EXPECTED GOT ""
printf '  %s\n' "$(printf '%.0s-' $(seq 1 84))"

for f in "$HERE"/fixtures/*.desc "$HERE"/real-descriptors/*.desc; do
  [ -e "$f" ] || continue
  name=$(basename "$f" .desc)
  case "$f" in *real-descriptors*) name="REAL $name";; esac
  [ -n "$FILTER" ] && case "$name" in *"$FILTER"*) ;; *) continue;; esac
  want=$(sed -n 's/^#!expect=//p' "$f" | head -1)
  if [ -z "$want" ]; then
    printf '  %-46s %-14s %-14s %s\n' "$name" "-" "-" "SKIP no #!expect header"
    skip=$((skip+1)); continue
  fi
  # A descriptor captured from a device arrives with #!expect set to whatever the
  # CLASSIFIER guessed. Asserting on that tests nothing: it freezes today's answer
  # as tomorrow's requirement. Only descriptors carrying #!ground_truth -- meaning
  # a human named the device independently -- are allowed to assert. The rest stay
  # in the folder as evidence. See tests/promote.py.
  case "$f" in *real-descriptors*)
    if ! grep -q '^#!ground_truth=' "$f"; then
      printf '  %-46s %-14s %-14s %s\n' "$name" "$want" "-" "SKIP no ground truth"
      skip=$((skip+1)); continue
    fi ;;
  esac
  got=$(ADB_STATE="" bash "$CLASSIFY" < "$f" | awk -F'\t' '$1=="class"{print $2}')
  if [ "$got" = "$want" ]; then
    printf '  %-46s %-14s %-14s %s\n' "$name" "$want" "$got" "ok"
    pass=$((pass+1))
  else
    printf '  %-46s %-14s %-14s %s\n' "$name" "$want" "$got" "FAIL"
    fail=$((fail+1))
  fi
done

if [ -z "$FILTER" ]; then
  TMP_TEST="$(mktemp -d /tmp/bench-test.XXXXXX)"
  mkdir -p "$TMP_TEST/bin" "$TMP_TEST/bench"

  cat <<'EOF' > "$TMP_TEST/bin/sudo"
#!/usr/bin/env bash
shift
"$@"
EOF
  chmod +x "$TMP_TEST/bin/sudo"

  cat <<'EOF' > "$TMP_TEST/bin/apt"
#!/usr/bin/env bash
exit 0
EOF
  chmod +x "$TMP_TEST/bin/apt"

  cat <<'EOF' > "$TMP_TEST/bin/adb"
#!/usr/bin/env bash
exit 0
EOF
  chmod +x "$TMP_TEST/bin/adb"

  cat <<'EOF' > "$TMP_TEST/bin/fastboot"
#!/usr/bin/env bash
exit 0
EOF
  chmod +x "$TMP_TEST/bin/fastboot"

  # Fake lsusb: outputs mouse + USB stick
  cat <<'EOF' > "$TMP_TEST/bin/lsusb"
#!/usr/bin/env bash
if [ "${1:-}" = "-v" ]; then
  echo "Bus 001 Device 003: ID 0781:5583 SanDisk Corp. Ultra Fit"
  echo "      bInterfaceClass         8 Mass Storage"
  exit 0
fi
echo "Bus 001 Device 002: ID 046d:c52b Logitech, Inc. Unifying Receiver"
echo "Bus 001 Device 003: ID 0781:5583 SanDisk Corp. Ultra Fit"
EOF
  chmod +x "$TMP_TEST/bin/lsusb"

  # 1. 00-setup.sh baseline check: answering 'y' deletes baseline and exits 1
  SETUP_RC=0
  SETUP_OUT=$(printf '\ny\n' | HOME="$TMP_TEST" PATH="$TMP_TEST/bin:$PATH" bash "$HERE/../bench-kit/scripts/00-setup.sh" 2>&1) || SETUP_RC=$?
  if [ "$SETUP_RC" -eq 1 ] && \
     printf '%s' "$SETUP_OUT" | grep -q "Is the phone or tablet you are about to test in this list?" && \
     printf '%s' "$SETUP_OUT" | grep -q "Unplug it, then run bash 00-setup.sh again" && \
     [ ! -f "$TMP_TEST/bench/baseline.txt" ]; then
    printf '  %-46s %-14s %-14s %s\n' "00-setup.sh baseline prompt [y]" "exit 1, del" "exit 1, del" "ok"
    pass=$((pass+1))
  else
    printf '  %-46s %-14s %-14s %s\n' "00-setup.sh baseline prompt [y]" "exit 1, del" "failed" "FAIL"
    fail=$((fail+1))
  fi

  # 2. 01-detect.sh: multi-device prompt when diff > 1
  echo "Bus 001 Device 002: ID 046d:c52b Logitech, Inc. Unifying Receiver" > "$TMP_TEST/bench/baseline.txt"
  cat <<'EOF' > "$TMP_TEST/bin/lsusb"
#!/usr/bin/env bash
if [ "${1:-}" = "-v" ]; then
  echo "Bus 001 Device 003: ID 0781:5583 SanDisk Corp. Ultra Fit"
  echo "      bInterfaceClass         8 Mass Storage"
  exit 0
fi
echo "Bus 001 Device 002: ID 046d:c52b Logitech, Inc. Unifying Receiver"
echo "Bus 001 Device 003: ID 0781:5583 SanDisk Corp. Ultra Fit"
echo "Bus 001 Device 004: ID 18d1:4ee2 Google Inc. Nexus/Pixel Device"
EOF
  chmod +x "$TMP_TEST/bin/lsusb"

  DETECT_RC=0
  DETECT_OUT=$(printf '1\n' | HOME="$TMP_TEST" PATH="$TMP_TEST/bin:$PATH" bash "$HERE/../bench-kit/scripts/01-detect.sh" 2>&1) || DETECT_RC=$?
  if [ "$DETECT_RC" -eq 0 ] && \
     printf '%s' "$DETECT_OUT" | grep -q "More than one new device appeared:" && \
     printf '%s' "$DETECT_OUT" | grep -q "Which one is the device you are testing?"; then
    printf '  %-46s %-14s %-14s %s\n' "01-detect.sh multi-device prompt" "prompt & select" "prompt & select" "ok"
    pass=$((pass+1))
  else
    printf '  %-46s %-14s %-14s %s\n' "01-detect.sh multi-device prompt" "prompt & select" "failed" "FAIL"
    fail=$((fail+1))
  fi

  # 3. 01-detect.sh: empty diff message
  cat <<'EOF' > "$TMP_TEST/bin/lsusb"
#!/usr/bin/env bash
echo "Bus 001 Device 002: ID 046d:c52b Logitech, Inc. Unifying Receiver"
EOF
  chmod +x "$TMP_TEST/bin/lsusb"

  EMPTY_OUT=$(HOME="$TMP_TEST" PATH="$TMP_TEST/bin:$PATH" bash "$HERE/../bench-kit/scripts/01-detect.sh" 2>&1) || true
  if printf '%s' "$EMPTY_OUT" | grep -q "Nothing new since setup"; then
    printf '  %-46s %-14s %-14s %s\n' "01-detect.sh empty diff message" "helpful advice" "helpful advice" "ok"
    pass=$((pass+1))
  else
    printf '  %-46s %-14s %-14s %s\n' "01-detect.sh empty diff message" "helpful advice" "failed" "FAIL"
    fail=$((fail+1))
  fi

  rm -rf "$TMP_TEST"
  rm -rf "$HERE/../bench-kit/descriptors"
fi

echo
echo "  $pass passed, $fail failed, $skip skipped"
if [ "$skip" -gt 0 ]; then
  echo
  echo "  Skipped descriptors are real captures with no independent identity behind"
  echo "  them. They are kept as evidence and can be promoted later -- ask the tester"
  echo "  what the device was, then run: python3 tests/promote.py --write"
fi
if [ "$fail" -gt 0 ]; then
  echo
  echo "  A failure here is the classifier disagreeing with a device whose identity"
  echo "  a human established independently. Fix classify.sh, not the fixture --"
  echo "  unless the fixture's expected class was itself wrong, in which case say so"
  echo "  in a #!note and record why."
  echo
  exit 1
fi
echo
