#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
#
# The SECOND pass of a review. Never the first.
#
#     bash tests/review-carry.sh
#
# tests/review-packet.sh gives a reviewer a diff and nothing else, on purpose: an assistant
# that already knows what the work was meant to do will confirm that it did. That blindness
# is right for finding defects and useless for tracking them, because every review then
# begins and ends in the same session and nobody notices a finding nobody fixed.
#
# So: the blind review answers first. Its findings go into docs/reference/review-log.md as
# checkboxes. THEN this runs, and asks the same session one more question -- are these
# still true? A finding that survives three reviews has stopped being a finding and become
# a decision, and it belongs in the tracker rather than in this log.
#
# Order matters. Run this before the blind answer is in and the review is no longer blind.
set -u
cd "$(git rev-parse --show-toplevel)" || exit 1
LOG="docs/reference/review-log.md"

if [ ! -f "$LOG" ]; then
  echo "no $LOG yet -- nothing has been reviewed, or nothing was written down"
  exit 0
fi

# Unticked findings, oldest first, each with the review heading it came from.
open_count=$(grep -c '^- \[ \]' "$LOG" 2>/dev/null || echo 0)

echo "===== CARRIED FINDINGS  $(date -u +%Y-%m-%dT%H:%MZ) ====="
if [ "$open_count" -eq 0 ]; then
  echo "Nothing outstanding. Every finding in $LOG is ticked."
  echo
  echo "That is only good news if the log has entries. It has:"
  grep -c '^## ' "$LOG" | sed 's/^/  /'
  echo "  review(s) recorded."
  exit 0
fi

awk '
  /^## / { head=$0 }
  /^- \[ \]/ {
    if (head != last) { print ""; print head; last=head }
    print "  " $0
  }
' "$LOG"

echo
echo "===== ASK ONLY THIS ====="
cat <<'ASK'
You have just reviewed this diff blind. Above are findings from EARLIER reviews that were
never ticked off. For each one, and only from what is in the diff and the files it touches:

  a. Is it fixed? Cite the line that fixes it.
  b. Is it still true? Cite the line that still has it.
  c. Is it no longer meaningful, because the code around it changed?

Do not re-open a finding you cannot see evidence for. Do not tick anything yourself --
say which, and the log gets updated by hand.
ASK
echo
echo "$open_count finding(s) carried. Three reviews and still open means it is a decision,"
echo "not a finding: move it to the tracker."
