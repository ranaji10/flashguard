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

## Step 5 — read the answer, applying one test

The reviewer will produce five numbered answers, because the packet ends with five
questions. You are not judging whether they sound right. Assistants are fluent, and a
fluent wrong answer is the failure this whole arrangement exists to prevent.

**The one test: can you click on it?**

Every finding should name a file and a line you can open. Open one. If the line is there
and says what the review says it says, the finding is real, whether or not you agree it
matters. If you open the file and the line is not there, or says something else, the
review invented it.

A finding you can act on looks like this:

> 2. `data/coverage.py:88` computes the information-loss rate as `loss / total` with no
> guard for `total == 0`. An empty corpus prints `0%`, which reads as "no loss" rather
> than "nothing measured".

A finding you cannot act on looks like this:

> 2. The coverage calculation may not handle edge cases robustly, and error handling could
> be improved for better maintainability.

The second one names nothing. There is nothing to open, nothing to fix, and nothing to
tick off later. It is the sound of a reviewer that found nothing and did not want to say
so. Ignore it entirely.

**One thing to check that is easy to miss: where did it get that?**

The first real review through this workflow opened with *"the commit message says..."* and
quoted it accurately. The commit message is **not in the packet** — it was left out on
purpose. The reviewer had a shell, ran `git log`, and read the producer's own account of the
change before answering question 1, which asks what changed that was *not* asked for. You
cannot answer that from the document that says what was asked for.

It was not wrong about anything, and the review was a good one. But the packet now tells the
reviewer plainly not to read the commit message, the log, or any file explaining why. Reading
the repository to understand a changed line is expected. Reading the rationale is not.

If a review quotes the commit message, it went outside the packet. That is worth noticing
even when the answer is right, because the next time it may be right for the wrong reason.

**Three specific things that mean the session is bad and should be discarded:**

- It reports build status. The packet says "Do NOT report build status: the suite above
  already did that." If it opens with "the build passes", it did not read its
  instructions, and everything after that is guesswork.
- It describes something that is not in the diff. The packet contains a specific set of
  changed lines. A claim about a file that was not touched is a claim from memory.
- It says everything is fine in three sentences. A real "I found nothing" cites what it
  checked. "Nothing found" alone means it did not look.

If any of those happen: quit the CLI, start again, paste the same packet. Do not argue
with it and do not ask follow-up questions. A session that answered from the wrong place
once will keep doing it, and each exchange makes it more confident.

**"It found nothing" is a legitimate result.** Most reviews of a small, careful change
should find nothing. If your reviewer finds three problems every single time, it is
inventing them to be useful, and the log will fill with noise until you stop reading it.

---

## Step 6 — write the findings into the log

Open the file:

```
open -a "Visual Studio Code" docs/reference/review-log.md
```

or just click it in the VS Code sidebar.

Add a heading at the **top**, above the previous review, and one line per finding:

```
## 2026-09-14 — 4bb57e3 — verdict field split
- [ ] `data/coverage.py:88` information-loss rate divides by zero on an empty corpus,
      so 0 of 0 prints as 0% and reads as "no loss"
- [ ] `data/recipes/fp4-independent-facts.json:5` both verdict fields set to unsafe
      with no differs_because
```

Rules that make this work rather than decorate:

- **The date and the commit hash.** The hash is in the packet's first lines
  (`reviewing: the last commit, 4bb57e3`). Without it you cannot tell later which state of
  the code a finding was about.
- **One `- [ ]` per finding.** The box is the whole mechanism. Anything not in a box is
  invisible to `review-carry.sh`.
- **Copy the file and line the review cited.** Not your paraphrase of the problem. In
  three weeks you will not remember which line it meant, and the reviewer that reads it
  next will not either.
- **A wrapped finding is fine.** Indent the continuation lines and they stay part of the
  same finding.
- **Record an empty review too.** Put the heading in with no boxes under it. A log that
  only contains reviews that found something will convince you, wrongly, that every review
  finds something.

**Only you tick a box.** Not Copilot, not the reviewer, not me. The box means *a human
looked and agreed it is done*, and the moment an assistant can tick it, it means nothing.

---

## Step 7 — the second pass, into the same session

Now, and not before:

```
bash tests/review-carry.sh
```

It prints every unticked finding from **earlier** reviews, oldest first, with how many
reviews each has survived:

```
===== CARRIED FINDINGS  2026-09-14T09:12Z =====

## 2026-09-06 — 250698b — corpus replay  (carried through 2 later reviews)
  - [ ] `docs/reasoning/safe-case.md:39` the DISPUTED marker has no owner and no date

## 2026-09-09 — 8a21887 — review ritual  (newest review)
  - [ ] `tests/review-packet.sh:41` the suite grep drops a FAIL line containing a colon

===== ASK ONLY THIS =====
...
```

Copy all of it and paste into the **same** CLI session you just used — the one that has
already given you its blind answer. Not a new one.

**Why the same session, when the first pass demanded a fresh one.** The first pass has to
be blind so the reviewer reads the diff instead of a list of expected problems. By now it
has read the diff and committed to an answer, so it cannot un-see it. It is the cheapest
possible reader for "are these old findings still true", because it already has the
current code in view. Giving the carried list to a *new* session would mean paying for it
to read everything again, and giving it to the *first* session before it answered would be
handing it the answers.

It will reply for each carried finding: fixed and here is the line, still true and here is
the line, or no longer meaningful because the surrounding code changed. Then **you** go and
tick, in the log, the ones where it showed you the fix. Change `- [ ]` to `- [x]` and add
a short note:

```
- [x] `tests/review-packet.sh:41` grep drops a FAIL line with a colon — fixed in 316e08d
```

If it says a finding is no longer meaningful, tick it with the reason rather than deleting
it. Deleting loses the fact that it was ever raised, which is the one thing this file is
for.

---

## Step 8 — the rule that stops the log rotting

**Anything that has survived three reviews is not a finding. It is a decision.**

`review-carry.sh` prints a line above such items so you cannot miss it:

```
  >>> SURVIVED 2 REVIEWS. This is a decision now, not a finding.
```

A finding survives three reviews for one reason: nobody has decided what to do about it.
Sometimes that is because it needs a judgement only you can make, sometimes because fixing
it means changing something bigger, and sometimes because it was never important. All three
are decisions, and none of them belong in a review log, because the log is read by an
assistant looking for defects and it will keep re-reporting them.

What to do:

1. Add it to the tracker as a proper item with a body saying where it stands.
2. Tick it in the log with `moved to tracker`.

Example: `docs/reasoning/safe-case.md:39` carries an open `DISPUTED:` marker about whether
`variant` mismatch is a verifier concept. No test can settle it. It needs your ruling. If a
review keeps flagging it, that is not the reviewer being thorough, it is the log holding a
question that has nowhere else to live.

**Why this matters more than it looks.** A checklist mechanism does not fail loudly. It
fills up, becomes tedious, gets skimmed, and then stops being read while still appearing to
run. That is the same shape as a test that passes because it never executed, and as a
publication scan with an exemption in it. This project has now produced both. The three-
review rule is the thing that keeps this one honest.

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
