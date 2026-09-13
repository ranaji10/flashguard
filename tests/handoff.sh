#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Print the handoff block to paste when moving between VS Code and a Claude session.
#
#     bash tests/handoff.sh
#
# WHY THIS EXISTS. Two assistants work on this repository and neither can see the other's
# conversation. Describing state in prose ("I fixed the classifier") invites both of them to
# be confident about something neither has checked. A commit SHA cannot be misremembered.
#
# Paste the output as the FIRST message of the receiving session.
set -u
cd "$(cd "$(dirname "$0")/.." && pwd)" || exit 1

sha=$(git rev-parse --short HEAD 2>/dev/null || echo "no-git")
branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "?")
dirty=$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')
ahead=$(git log --oneline @{u}..HEAD 2>/dev/null | wc -l | tr -d ' ')

echo
echo "--------------------------- HANDOFF ---------------------------"
echo "Read the repo at commit $sha on branch $branch, then continue."
echo
echo "  repo         github.com/ranaji10/flashguard"
echo "  commit       $sha"
[ "$dirty" != "0" ] && echo "  UNCOMMITTED  $dirty file(s) — commit before handing off, or say why not"
[ "$ahead" != "0" ] && echo "  UNPUSHED     $ahead commit(s) — the other side cannot see these yet"
echo
echo "  last 3 commits"
git log --oneline -3 2>/dev/null | sed 's/^/    /'
echo
echo "  OPEN.md last touched"
git log -1 --format='    %h  %an  %ad  %s' --date=short -- docs/open-items-snapshot.md 2>/dev/null
if git log -1 --format='%B' -- docs/open-items-snapshot.md 2>/dev/null | grep -q 'Co-Authored-By: Claude'; then
  echo "    last edited from a CLAUDE session"
else
  echo "    last edited from VS CODE (no Claude co-author trailer)"
fi
echo
echo "  suite"
# The suite has THREE outcomes and this used to have two. Exit 2 is decisions waiting --
# an open disagreement, an unfilled tester placeholder -- and reporting it as SUITE FAILING
# sent a reader hunting for a defect that was not there. On 13 September a reviewer spent
# part of a handoff explaining that a "FALSE SAFE: 1 -- BUILD MUST FAIL" line was "test
# noise", which it was, because the gate's own test prints it. Explaining away a false-safe
# message is the most dangerous habit this project could acquire, and the reason it had to
# be explained was this branch.
bash tests/all.sh >/tmp/handoff-suite.$$ 2>&1; rc=$?
case "$rc" in
  0)
    grep -hE '[0-9]+ passed|tracked files|all indexed' /tmp/handoff-suite.$$ | sed 's/^ */    /'
    ;;
  2)
    echo "    suite green. Decisions waiting, which do not block a handoff:"
    grep -hE 'OPEN DISAGREEMENT|PLACEHOLDERS still' /tmp/handoff-suite.$$ | head -4 | sed 's/^ */      /'
    echo "    The line \"FALSE SAFE: 1 -- BUILD MUST FAIL\" appears in a passing run: the"
    echo "    gate's own test plants one and asserts the build fails. It is the gate working."
    ;;
  *)
    echo "    SUITE FAILING — fix before handing off:"
    grep -hE 'FAIL|BANNED|DANGLING|ORPHAN|BROKEN|DIVERGED' /tmp/handoff-suite.$$ | head -5 | sed 's/^ */      /'
    ;;
esac
rm -f /tmp/handoff-suite.$$
echo
echo "  Tier A"
python3 data/coverage.py 2>/dev/null | sed -n '/TIER A/,/^$/p' | sed 's/^/  /'
echo "---------------------------------------------------------------"
echo
echo "Do not describe what you did. The commit is the description."
echo
