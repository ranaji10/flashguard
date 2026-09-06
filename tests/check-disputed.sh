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
# the marker. A DISPUTED marker with a nameable test is laziness, not honesty.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"; ROOT="$(cd "$HERE/.." && pwd)"
cd "$ROOT" || exit 1

hits=$(git grep -n 'DISPUTED:' -- . 2>/dev/null | grep -v 'check-disputed' | grep -v 'copilot-instructions' || true)
[ -z "$hits" ] && exit 0

n=$(printf '%s\n' "$hits" | wc -l | tr -d ' ')
echo "  $n OPEN DISAGREEMENT(S) needing your decision, not an assistant's:"
printf '%s\n' "$hits" | cut -c1-160 | sed 's/^/      /'
echo "      Each needs a ruling from you. If a test would settle it, write the test."
exit 2
