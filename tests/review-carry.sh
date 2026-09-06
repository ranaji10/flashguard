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
# grep -c prints 0 and exits 1 when nothing matches, so '|| echo 0' would append a SECOND
# zero and the arithmetic below would see "0\n0". Swallow the status, keep grep's count.
open_count=$(grep -c '^- \[ \]' "$LOG" 2>/dev/null) || true
open_count=${open_count:-0}

echo "===== CARRIED FINDINGS  $(date -u +%Y-%m-%dT%H:%MZ) ====="
if [ "$open_count" -eq 0 ]; then
  echo "Nothing outstanding. Every finding in $LOG is ticked."
  echo
  echo "That is only good news if the log has entries. It has:"
  reviews=$(grep -c '^## 20' "$LOG" 2>/dev/null) || true
  echo "  ${reviews:-0} review(s) recorded. Zero means nothing has been reviewed yet, or"
  echo "  a review happened and its findings were never written down."
  exit 0
fi

# Findings are collected whole -- a finding wrapped over several lines is one finding, and
# printing only its first line hands the reviewer half a sentence. Sections come out OLDEST
# FIRST, because age is the thing being judged, and the log itself is newest-first.
awk '
  /^## / {
    n++; head[n]=$0; body[n]=""; next
  }
  /^- \[ \]/ {
    cur=n; body[n]=body[n] "\n  " $0; open[n]++; next
  }
  /^- \[[xX]\]/ { cur=0; next }
  /^[[:space:]]+[^[:space:]]/ {
    # a wrapped continuation of the finding above it
    if (cur==n && open[n]>0) body[n]=body[n] "\n  " $0
    next
  }
  { cur=0 }
  END {
    for (i=n; i>=1; i--) {
      if (open[i]>0) {
        later=i-1   # sections above it in the file are the NEWER reviews
        age = later==0 ? "(newest review)" \
                       : "(carried through " later " later review" (later==1?"":"s") ")"
        print ""
        if (later>=2) print "  >>> SURVIVED " later " REVIEWS. This is a decision now, not a finding."
        print head[i] "  " age
        print substr(body[i],2)
      }
    }
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
