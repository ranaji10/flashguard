#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Build the packet to hand a REVIEWING assistant. One command, so the review ritual is
# cheap enough to actually happen.
#
#     bash tests/review-packet.sh | pbcopy
#
# PIPED TO pbcopy IT PRINTS NOTHING TO THE SCREEN, because that is what a pipe does: the
# packet goes to the clipboard, not to the terminal. A confirmation line goes to stderr so
# the terminal is never silent. Drop the pipe to read it instead:
#
#     bash tests/review-packet.sh | less
#
# It ends with the five questions. Those are the whole point: an assistant asked "does
# this look right?" says yes. An assistant asked "what did this decide that was not in a
# file?" has to go and look.
#
# WHICH SIDE OF THE COMMIT. It works out. A dirty tree means the work is uncommitted, so
# it diffs against HEAD. A clean tree means the work is already committed, so it diffs the
# last commit. Pass a ref to override:  bash tests/review-packet.sh HEAD~3
#
# The recommended habit is COMMIT, DO NOT PUSH, THEN REVIEW. Committing makes the work
# safe from a crash or a stray undo and gives the reviewer a stable reference, which is
# what docs/reference/handoff.md asks for. Not pushing keeps history fixable: amend or
# revert costs nothing until someone else has the commit.
set -u
cd "$(git rev-parse --show-toplevel)" || exit 1

if [ $# -ge 1 ]; then
  BASE="$1"; WHERE="explicit range $BASE..HEAD"
elif [ -n "$(git status --porcelain)" ]; then
  BASE="HEAD";   WHERE="uncommitted work in the tree"
else
  BASE="HEAD~1"; WHERE="the last commit, $(git log -1 --format=%h)"
fi

echo "===== REVIEW PACKET  $(date -u +%Y-%m-%dT%H:%MZ) ====="
echo "reviewing: $WHERE"
echo
echo "--- suite ---"
bash tests/all.sh 2>&1 | grep -E 'passed|failed|indexed|tracked files|NOT IMPLEMENTED|PLACEHOLDER|DISAGREEMENT|FAIL' | sed 's/^/  /'
echo
echo "--- files touched ---"
git diff --stat "$BASE" | sed 's/^/  /'
echo
echo "--- diff ---"
git diff "$BASE"
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

Do NOT read the commit message, the commit log, or any file describing why this change was
made. They are the producer's own account of the work, and this packet leaves them out on
purpose. Question 1 asks what changed that was not asked for; you cannot answer it from the
document that says what was asked for. The diff is the subject. Reading the repository to
understand a changed line is expected; reading the rationale is not.

FINISH WITH THIS BLOCK, exactly, so it can be filed without being retyped:

  FINDINGS
  - [ ] `path/to/file.py:88` what is wrong, in one sentence, wrapped and indented
        under itself if it needs a second line
  - [ ] `path/to/other.sh:12` the next one

One unticked box per finding, each naming a file and a line. NEVER write a ticked box:
only a person ticks, and a reviewer that ticks its own findings has marked its own
homework. If you found nothing, write FINDINGS and then "none" -- an empty review is a
result, and a log of only non-empty reviews is a biased log.
ASK

# stderr, so it survives '| pbcopy' and is never captured into the packet itself
{
  echo
  echo "  review packet built: $WHERE"
  echo "  $(git diff --stat "$BASE" | tail -1 | sed 's/^ *//')"
  echo "  If you piped this to pbcopy it is on the clipboard now. Paste it into a FRESH"
  echo "  session as the first and only message. No summary, no context, nothing after it."
} >&2
