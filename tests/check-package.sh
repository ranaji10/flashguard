#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Check tester package build, contents against MANIFEST, and SHA256 checksums.
set -u

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"

TMP_DIR="$(mktemp -d /tmp/flashguard-check-pkg.XXXXXX)"
trap 'rm -rf "$TMP_DIR"' EXIT

bash "$ROOT/tools/build-package.sh" --skip-suite --out-dir "$TMP_DIR" >/dev/null 2>&1 || {
  echo "  check-package: build-package.sh failed"
  exit 1
}

ZIP=$(find "$TMP_DIR" -name "flashguard-tester-kit-*.zip" | head -1)
if [ -z "$ZIP" ] || [ ! -f "$ZIP" ]; then
  echo "  check-package: package zip was not created"
  exit 1
fi

mkdir -p "$TMP_DIR/extracted"
unzip -q "$ZIP" -d "$TMP_DIR/extracted"

PKG_DIR="$TMP_DIR/extracted/flashguard-tester-kit"
if [ ! -d "$PKG_DIR" ]; then
  echo "  check-package: zip top-level directory flashguard-tester-kit/ missing"
  exit 1
fi

if [ ! -f "$PKG_DIR/SHA256SUMS.txt" ]; then
  echo "  check-package: SHA256SUMS.txt missing from package root"
  exit 1
fi

# Verify checksums
(
  cd "$PKG_DIR"
  if command -v shasum >/dev/null 2>&1; then
    shasum -a 256 -c SHA256SUMS.txt >/dev/null 2>&1 || { echo "  check-package: SHA256 checksum verification failed"; exit 1; }
  elif command -v sha256sum >/dev/null 2>&1; then
    sha256sum -c SHA256SUMS.txt >/dev/null 2>&1 || { echo "  check-package: SHA256 checksum verification failed"; exit 1; }
  else
    echo "  check-package: no shasum/sha256sum available"
    exit 1
  fi
) || exit 1

# Check MANIFEST equality
MANIFEST="$ROOT/bench-kit/MANIFEST.txt"
PKG_FILES=$(cd "$PKG_DIR" && find . -type f | sed 's|^\./||' | sort)

# Build expected file list from MANIFEST + SHA256SUMS.txt
EXPECTED_FILES=$(
  while IFS= read -r line || [ -n "$line" ]; do
    trimmed=$(echo "$line" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')
    [ -z "$trimmed" ] && continue
    if [ "$trimmed" = "# excluded:" ]; then
      break
    fi
    case "$trimmed" in
      ( "#"* ) continue ;;
      ( * ) echo "$trimmed" ;;
    esac
  done < "$MANIFEST"
  echo "SHA256SUMS.txt"
)
EXPECTED_FILES=$(printf '%s\n' "$EXPECTED_FILES" | sort)

if [ "$PKG_FILES" != "$EXPECTED_FILES" ]; then
  echo "  check-package: packaged files differ from MANIFEST + SHA256SUMS.txt"
  echo "  Packaged:"
  echo "$PKG_FILES" | sed 's/^/    /'
  echo "  Expected:"
  echo "$EXPECTED_FILES" | sed 's/^/    /'
  exit 1
fi

# Verify stamped KIT_VERSION
TODAY=$(date +%Y-%m-%d)
if ! grep -q "var KIT_VERSION = \"$TODAY\";" "$PKG_DIR/START-HERE.html"; then
  echo "  check-package: KIT_VERSION was not stamped with today's date ($TODAY) in START-HERE.html"
  exit 1
fi

echo "  package structure, checksums and KIT_VERSION verified"
