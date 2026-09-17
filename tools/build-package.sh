#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Build the tester distribution package with SHA256 checksums.
set -u

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"

SKIP_SUITE=0
OUT_DIR="$ROOT/dist"

while [ $# -gt 0 ]; do
  case "$1" in
    --skip-suite)
      SKIP_SUITE=1
      shift
      ;;
    --out-dir)
      OUT_DIR="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

if [ "$SKIP_SUITE" -eq 0 ]; then
  echo "Running test suite before packaging..."
  bash "$ROOT/tests/all.sh" || { echo "Test suite failed. Packaging aborted."; exit 1; }
fi

MANIFEST="$ROOT/bench-kit/MANIFEST.txt"
if [ ! -f "$MANIFEST" ]; then
  echo "Error: MANIFEST.txt missing at $MANIFEST"
  exit 1
fi

if command -v shasum >/dev/null 2>&1; then
  SHACMD="shasum -a 256"
elif command -v sha256sum >/dev/null 2>&1; then
  SHACMD="sha256sum"
else
  echo "Error: neither shasum nor sha256sum available"
  exit 1
fi

# Parse MANIFEST for included and excluded files
INCLUDED=""
EXCLUDED=""
IN_EXCLUDED=0

while IFS= read -r line || [ -n "$line" ]; do
  trimmed=$(echo "$line" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')
  [ -z "$trimmed" ] && continue

  if [ "$trimmed" = "# excluded:" ]; then
    IN_EXCLUDED=1
    continue
  fi

  if [ "$IN_EXCLUDED" -eq 1 ]; then
    # Excluded file line (may start with #)
    ex_file=$(echo "$trimmed" | sed -e 's/^#[[:space:]]*//' -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')
    [ -n "$ex_file" ] && EXCLUDED="$EXCLUDED $ex_file"
  else
    case "$trimmed" in
      "#"*) continue ;;
      *) INCLUDED="$INCLUDED $trimmed" ;;
    esac
  fi
done < "$MANIFEST"

# 1. Verify every MANIFEST path exists in bench-kit/
for f in $INCLUDED; do
  if [ ! -f "$ROOT/bench-kit/$f" ]; then
    echo "Error: MANIFEST file missing on disk: bench-kit/$f"
    exit 1
  fi
done

# 2. Verify all files in bench-kit/ are in MANIFEST or EXCLUDED
while IFS= read -r disk_file; do
  rel="${disk_file#$ROOT/bench-kit/}"
  case "$rel" in
    .DS_Store|*/.DS_Store) continue ;;
  esac

  found=0
  for inc in $INCLUDED; do
    if [ "$inc" = "$rel" ]; then
      found=1
      break
    fi
  done

  if [ "$found" -eq 0 ]; then
    for exc in $EXCLUDED; do
      case "$rel" in
        "$exc"|"$exc"/*|"$exc"*)
          found=1
          break
          ;;
      esac
    done
  fi

  if [ "$found" -eq 0 ]; then
    echo "Error: Unmanifested file in bench-kit/: $rel (must be in MANIFEST.txt or under # excluded:)"
    exit 1
  fi
done < <(find "$ROOT/bench-kit" -type f)

TODAY=$(date +%Y-%m-%d)
STAGE="$(mktemp -d /tmp/flashguard-pkg.XXXXXX)"
PKG_DIR="$STAGE/flashguard-tester-kit"
mkdir -p "$PKG_DIR"

for f in $INCLUDED; do
  target_dir="$PKG_DIR/$(dirname "$f")"
  mkdir -p "$target_dir"
  cp "$ROOT/bench-kit/$f" "$PKG_DIR/$f"
done

# Stamp KIT_VERSION in copy of START-HERE.html
sed -i.bak "s/var KIT_VERSION = \".*\";/var KIT_VERSION = \"$TODAY\";/" "$PKG_DIR/START-HERE.html"
rm -f "$PKG_DIR/START-HERE.html.bak"

# Generate SHA256SUMS.txt
(
  cd "$PKG_DIR"
  find . -type f ! -name SHA256SUMS.txt | sed 's|^\./||' | sort | while IFS= read -r f; do
    $SHACMD "$f"
  done > SHA256SUMS.txt
)

mkdir -p "$OUT_DIR"
ZIP_PATH="$OUT_DIR/flashguard-tester-kit-$TODAY.zip"
rm -f "$ZIP_PATH"

(
  cd "$STAGE"
  zip -q -r "$ZIP_PATH" "flashguard-tester-kit"
)

ZIP_SHA=$($SHACMD "$ZIP_PATH" | awk '{print $1}')
echo "Package built: $ZIP_PATH"
echo "SHA256: $ZIP_SHA"

rm -rf "$STAGE"
