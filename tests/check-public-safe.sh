#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
#
# What would become public if this repository were flipped today.
#
# It scans TRACKED files only, because untracked and gitignored files never leave the
# machine. That is the actual question: not "what is in the folder" but "what would GitHub
# get". Run it before flipping to public, and it runs in the suite so the answer is never
# more than one commit old.
#
# It cannot judge whether a sentence is unwise. It catches the mechanical leaks: an address,
# a home path, a credential, a serial number, a name that belongs to someone who did not
# sign up for this.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"; ROOT="$(cd "$HERE/.." && pwd)"
cd "$ROOT" || exit 1
fail=0

look(){ # label, pattern, [allowlist regex]
  local label="$1" pat="$2" alw="${3:-}"
  local hits
  hits=$(git grep -nIiE "$pat" -- . 2>/dev/null | grep -v '^docs/open-items-snapshot.md:' || true)
  [ -n "$alw" ] && hits=$(printf '%s\n' "$hits" | grep -viE "$alw" || true)
  if [ -n "$hits" ]; then
    echo "  $label"
    printf '%s\n' "$hits" | head -8 | cut -c1-150 | sed 's/^/      /'
    fail=1
  fi
}

# Credentials. No allowlist: the GPL text and the tester instructions legitimately say
# "password", so they are excluded by phrase rather than by pattern.
look "CREDENTIAL"        "ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|BEGIN [A-Z ]*PRIVATE KEY|api[_-]?key[\"' ]*[:=]"
look "PERSONAL EMAIL"    "[a-z0-9._%+-]+@(gmail|outlook|hotmail|yahoo|icloud|proton|seznam)\."
look "HOME PATH"         "/Users/[a-z]|/home/[a-z]" "home/claude|\\\$HOME"
look "DEVICE SERIAL"     "^[[:space:]]*iSerial[[:space:]]+[0-9]+[[:space:]]+[A-Za-z0-9]{6,}"
look "IMEI-SHAPED"       "(^|[^0-9])[0-9]{15}([^0-9]|$)"
look "MAC-SHAPED"        "\b([0-9a-f]{2}:){5}[0-9a-f]{2}\b"
look "THIRD PARTY NAME"  "\bAnna\b|\bUNDP\b|\bIPSA\b"

# Borrowed material must never cross the wall.
if git ls-files | grep -q '^library/'; then
  echo "  LIBRARY MATERIAL IS TRACKED. Borrowed, differently-licensed content cannot enter"
  echo "  this repository. See CLAUDE.md."
  fail=1
fi

if [ "$fail" = 0 ]; then
  echo "  $(git ls-files | wc -l | tr -d ' ') tracked files: no credential, personal address, serial or borrowed material"
fi
exit "$fail"
