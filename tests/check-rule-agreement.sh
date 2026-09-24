#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
#
# CLAUDE.md is the source of truth for the never-run list. The Copilot instruction files
# restate the rules for a different assistant, and a paraphrase drifted once already
# ("verify() does not exist" survived after verify.py was committed). This check is
# VERBATIM on purpose: every line of the indented block under "## Never run these" in
# CLAUDE.md must appear, character for character, in each file listed below.
# Self-test: bash check-rule-agreement.sh --self-test plants a divergence and expects exit 1.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
SRC="$ROOT/CLAUDE.md"
TARGETS="$ROOT/.github/copilot-instructions.md $ROOT/.github/copilot-review-instructions.md"

extract() {
  awk '/^## Never run these/{f=1;next} f&&/^## /{exit} f&&/^    [^ ]/{sub(/^    /,"");print}' "$1"
}

check() {
  src="$1"; shift
  lines=$(extract "$src")
  [ -n "$lines" ] || { echo "  no never-run block found in $src"; return 1; }
  fail=0
  for t in "$@"; do
    while IFS= read -r line; do
      [ -z "$line" ] && continue
      if ! grep -qF -- "$line" "$t"; then
        echo "  MISSING in ${t#$ROOT/}: $line"
        fail=1
      fi
    done <<< "$lines"
  done
  return $fail
}

if [ "${1:-}" = "--self-test" ]; then
  tmp=$(mktemp -d)
  printf '## Never run these\n\n    fastboot flash ...            planted-command-xyz\n\n## Next\n' > "$tmp/src.md"
  printf 'fastboot flash ...\n' > "$tmp/t.md"
  if check "$tmp/src.md" "$tmp/t.md" >/dev/null; then
    echo "  check-rule-agreement self-test FAILED: a divergence passed"; exit 1
  fi
  echo "  check-rule-agreement self-test passed"; exit 0
fi

# shellcheck disable=SC2086
if check "$SRC" $TARGETS; then
  echo "  never-run list identical in CLAUDE.md and both Copilot instruction files"
  exit 0
fi
exit 1
