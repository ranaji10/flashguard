#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Surface disagreements that no test can settle.
#
# When two assistants, or an assistant and Ranaji, disagree and the suite cannot decide,
# the honest move is neither to argue nor to pick quietly. It is to mark the question and
# put it in front of a person.
#
#     # DISPUTED: <the question>
#     #   position A: ...
#     #   position B: ...
#     #   settles it: <the test that would, or "no test can — needs a decision">
#
# Exit 2, loud, not build-failing: a disagreement is a decision waiting, not a defect.
# The rule that makes this work: if a test COULD settle it, write the test instead of
# the marker. A marker with a nameable test is laziness, not honesty.
#
# WHAT A MARKER IS. The first non-space characters on the line are a comment opener and
# then the word. That is what a marker looks like everywhere it is really used, and it is
# what stops this check from firing on prose that merely DISCUSSES the convention.
#
# It used to match the bare word anywhere on any line, with two filenames excluded by
# substring. On 6 September a reference document explaining the convention started
# reporting itself as an open disagreement, and the fix was to reword the document to get
# past the grep. That is the document being edited to satisfy the checker rather than the
# checker being made correct, and the next document to explain the convention would have
# hit it again. Same family as the publication scan that exempted the only file that could
# fail it: the exemption was invisible, so the check looked stricter than it was.
#
# The two paths still skipped are skipped by PATH, for a stated reason, and the skip is
# PRINTED. An exemption a reader cannot see is the part that does the damage.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"; ROOT="$(cd "$HERE/.." && pwd)"
cd "$ROOT" || exit 1

# Skipped, and said out loud: these two TEACH the convention, so they contain a specimen
# marker rather than a live disagreement.
SKIP='^(tests/check-disputed\.sh|\.github/copilot-instructions\.md):'

hits=$(git grep -nE '^[[:space:]]*[#/]+[[:space:]]*DISPUTED:' -- . 2>/dev/null \
       | grep -vE "$SKIP" || true)

if [ -z "$hits" ]; then
  echo "  no open disagreements (specimen markers in tests/check-disputed.sh and"
  echo "  .github/copilot-instructions.md are skipped: they teach the convention)"
  exit 0
fi

n=$(printf '%s\n' "$hits" | wc -l | tr -d ' ')
echo "  $n OPEN DISAGREEMENT(S) needing your decision, not an assistant's:"
printf '%s\n' "$hits" | cut -c1-160 | sed 's/^/      /'
echo "      Each needs a ruling from you. If a test would settle it, write the test."
echo "      (skipped, because they teach the convention rather than raise a question:"
echo "       tests/check-disputed.sh, .github/copilot-instructions.md)"
exit 2
