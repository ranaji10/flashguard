# The review workflow, step by step

*Every command, in order, with what each one should print. Follow it exactly the first few
times; after that it is two commands and a paste.*

The point of the whole ritual is one property: **the reviewer has never seen the work
before.** A session that already knows what the code was meant to do will agree that it
does. That is why nothing is ever summarised for it.

---

## Before you start

Copilot has finished a piece of work. Ask it to **commit but not push**. Committing makes
the work safe from a crash or a stray undo and gives the reviewer a fixed reference.
Not pushing keeps the history fixable: amend or revert costs nothing until someone else
has the commit.

---

## Step 1 — terminal: go to the project

```
cd ~/Repurpose/project
```

(`~` is your home folder. The publication scan refuses a literal home path in any
tracked file, which is why it is written this way.)

Every command below assumes you are here. Running `bash tests/review-packet.sh` from
inside `tests/` gives *No such file or directory*, because the path is relative to where
you are standing, not to where the script lives.

## Step 2 — terminal: build the packet

```
bash tests/review-packet.sh | pbcopy
```

**This deliberately prints almost nothing.** `pbcopy` is the macOS clipboard: the pipe
sends the packet there instead of to the screen. That is the whole job of `| pbcopy`, and
silence used to be the only sign it had worked. It now also prints a short confirmation:

```
  review packet built: the last commit, 8c8234e
  1 file changed, 7 insertions(+), 3 deletions(-)
  If you piped this to pbcopy it is on the clipboard now.
```

If you want to read the packet instead of copying it:

```
bash tests/review-packet.sh | less
```

`q` quits `less`.

The script works out which side of the commit to review on its own. A dirty tree means the
work is uncommitted, so it diffs against `HEAD`. A clean tree means the work is committed,
so it diffs the last commit. To review further back: `bash tests/review-packet.sh HEAD~3`.

## Step 3 — CLI: a genuinely fresh session

Quit the CLI and start it again. Not a new topic in the same session, not `/clear` if that
keeps history — **exit and restart.**

This is the step that matters most and the one it is most tempting to skip. The CLI has
reported a false clean state three times, once insisting the verifier did not exist while
118 committed lines of it sat on disk. The cause was never the model. It was a session
answering from what it had been told earlier rather than from what was in front of it.

## Step 4 — CLI: paste, and nothing else

Paste the clipboard as the **first and only** message.

- No summary of what Copilot did
- No "here is the context"
- No greeting, no framing, no follow-up sentence
- Do not paste the five questions separately; the packet already ends with them

The packet is built from `git diff` and the suite output, so it contains the changed lines
themselves rather than anyone's description of them. Adding a summary is what caused all
three false reports: the reviewer stops reading the diff and starts grading the account.

Press enter. Let it answer.

## Step 5 — read the answer with one test in mind

**Is every claim traceable to a line in the packet?**

A real finding cites a file and a line you can go and look at. A claim about something not
in the packet was invented, and the correct response is to discard the session and start
again rather than argue with it. Reviewers asked to find problems will produce problems.

The reviewer is also told not to report build status, because the suite already did. If it
opens with "the build passes", it did not read its instructions, which is itself a signal.

## Step 6 — write the findings down

Open `docs/reference/review-log.md` and add a heading, newest at the top:

```
## 2026-09-06 — 8c8234e — review-carry count fix
- [ ] `flashguard/verify.py:151` coverage reports safe_case_available with no
      explanation of what would change it
- [ ] `tests/all.sh:12` soft failure aggregated but the exit code is not propagated
```

One `- [ ]` per finding, with the file and line it cited. If the review found nothing, say
so under the heading with no boxes — an empty review is a result, and a log of only
non-empty reviews is a biased log.

**Only you tick a box.** No assistant ticks anything.

## Step 7 — the second pass, and only now

```
bash tests/review-carry.sh
```

This prints every finding from earlier reviews that is still unticked, oldest first, with
a short prompt. Paste that output into the **same** session you just used.

Order matters. Run this before the blind answer is in and the review is no longer blind:
the reviewer sees a list of known problems and starts looking for those instead of reading
the diff. It has to come second.

The session will tell you, for each carried finding, whether it is fixed, still true, or no
longer meaningful. Go and tick the ones it showed you the fix for.

## Step 8 — the rule that stops the log rotting

**A finding that survives three reviews has stopped being a finding and become a
decision.** Move it into the tracker as an item, and tick it in the log with a note saying
where it went. A log full of ancient open boxes is a log nobody reads, and then the
mechanism has quietly stopped working while still appearing to run.

---

## The short version, once it is habit

```
cd ~/Repurpose/project
bash tests/review-packet.sh | pbcopy      # then: fresh CLI, paste, nothing else
                                          # then: findings into review-log.md
bash tests/review-carry.sh                # paste into the SAME session, second
```

## What each file does

| File | Does |
|---|---|
| `tests/review-packet.sh` | Builds the blind packet: suite result, diff, five questions |
| `docs/reference/review-log.md` | What each review found; boxes ticked by hand only |
| `tests/review-carry.sh` | The second pass: unticked findings from earlier reviews |
| `.github/copilot-review-instructions.md` | The rules the reviewer is told to read first |
