#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Build the packet to hand a REVIEWING assistant. One command, so the review ritual is
# cheap enough to actually happen.
#
#     bash tests/review-packet.sh | pbcopy
#
# It ends with the five questions. Those are the whole point: an assistant asked "does
# this look right?" says yes. An assistant asked "what did this decide that was not in a
# file?" has to go and look.
set -u
cd "$(git rev-parse --show-toplevel)" || exit 1
echo "===== REVIEW PACKET  $(date -u +%Y-%m-%dT%H:%MZ) ====="
echo
echo "--- suite ---"
bash tests/all.sh 2>&1 | grep -E 'passed|failed|indexed|tracked files|NOT IMPLEMENTED|PLACEHOLDER|DISAGREEMENT|FAIL' | sed 's/^/  /'
echo
echo "--- files touched since HEAD ---"
git status --short | sed 's/^/  /'
echo
echo "--- diff ---"
git diff HEAD
echo
cat <<'ASK'
===== ANSWER ONLY THESE =====
You are reviewing another assistant's work. You do not write files.
Read .github/copilot-instructions.md and docs/reasoning/verifier-plan.md first.

1. What changed that was not asked for?
2. What did it decide that was not already in a file?
3. Does any test pass for a reason other than the code being correct?
4. Does any file, name or comment describe something as existing that does not?
5. Does anything here create a path to a false `safe`?

Cite lines. If you find nothing, say so plainly rather than inventing a concern.
Do NOT report build status: the suite above already did that.
ASK
