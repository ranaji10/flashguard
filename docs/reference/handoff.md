# Handing off between VS Code and a Claude session

*Two assistants work on this repository. Neither can see the other's conversation. This is
the protocol that stops both of them being confident about a state neither has checked.*

## The rule

**Do not describe what you did. Hand over a commit.**

"I fixed the classifier" is unverifiable and, worse, invites the receiving side to build on a
belief. `5f8cb0a` cannot be misremembered, cannot be half-true, and can be read.

    bash tests/handoff.sh

Paste the output as the first message of the receiving session. It prints the commit, the
branch, whether anything is uncommitted or unpushed, the last three commits, who last
touched the open items, the suite result and the Tier A scoreboard.

## Who does what

| | VS Code + Copilot | Claude session |
|---|---|---|
| Best at | Building. Whole-workspace edits, tight write-run-fix loops, no context ceiling. | Reading the live web, cross-file audits, arguing with a plan before it is built, sweeps. |
| Owns | The verifier, the corpus, tests, refactors, day-to-day code. | The open-items tracker, research against live sources, design review, this kind of protocol. |
| Rules it reads | `.github/copilot-instructions.md`, automatically | `CLAUDE.md`, automatically |

`CLAUDE.md` is the source of truth for rules. `.github/copilot-instructions.md` is the
abridged version. When one changes, change both.

## Provenance: who last touched the open items

Two mechanisms, one automatic and one a convention.

**Automatic.** Commits made from a Claude session carry a `Co-Authored-By: Claude` trailer.
Commits from VS Code do not. So:

    git log --format='%h %an %ad %s' -- docs/open-items-snapshot.md

tells you which side last wrote to the record, and `tests/handoff.sh` prints it for you in
plain words.

**Convention.** `docs/open-items-snapshot.md` is **generated** from the tracker. Nothing
should edit it directly. `tests/check-index.sh` fails if it drifts from `../OPEN.md`, which
is the same guard the two participation-note copies get.

To change the open items: edit the tracker, Export, drop the file over `~/Repurpose/OPEN.md`,
then `cp ../OPEN.md docs/open-items-snapshot.md` and commit. One direction only.

## Before handing off

1. Commit. An uncommitted change is invisible to the other side and `handoff.sh` says so.
2. Push, for the same reason.
3. `bash tests/all.sh` green. Handing off a failing suite hands off a debugging session.
4. If a decision was made in conversation, it is not made until it is in a file. Write it,
   index it, commit it. Otherwise it is lost at the session boundary — which is exactly how
   eleven decisions went unwritten before 6 September.
