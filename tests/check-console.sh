#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Parse-check START-HERE.html's script block.
#
# The console is one offline file that a tester runs with no network, no console
# open and no way to report a stack trace. A syntax error in it is a silent blank
# screen at the far end of a USB stick. This check takes 200ms and has already
# caught one broken edit.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
HTML="$HERE/../bench-kit/START-HERE.html"
JS="$(mktemp /tmp/bench-console.XXXXXX.js)"

python3 - "$HTML" "$JS" <<'PY'
import io,re,sys
s = io.open(sys.argv[1], encoding="utf-8").read()
blocks = re.findall(r"<script[^>]*>(.*?)</script>", s, re.S)
if not blocks:
    sys.exit("no <script> block found in " + sys.argv[1])
io.open(sys.argv[2], "w", encoding="utf-8").write("\n".join(blocks))
print("  %d script block(s), %d bytes" % (len(blocks), sum(len(b) for b in blocks)))
PY

if command -v node >/dev/null 2>&1; then
  node --check "$JS" && echo "  START-HERE.html parses" || { echo "  START-HERE.html DOES NOT PARSE"; exit 1; }
else
  echo "  node not installed, skipping parse check"
fi

for f in "$HERE"/../bench-kit/scripts/*.sh; do
  bash -n "$f" || { echo "  $(basename "$f") DOES NOT PARSE"; exit 1; }
done
echo "  all bench-kit scripts parse"
