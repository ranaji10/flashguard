# Review log

*What each blind review found, and whether it was ever fixed.*

**Why this exists.** `tests/review-packet.sh` hands a reviewer a diff and nothing else, so
that it reads the work rather than the producer's account of it. That blindness is right
for finding defects and useless for tracking them: every review began and ended in the
same session, and a finding nobody acted on simply vanished. This file is the memory the
reviewer is deliberately denied.

**How to use it.**

1. `bash tests/review-packet.sh | pbcopy` — paste into a fresh session as the first
   and only message. No summary, no context. Let it answer.
2. Paste its findings under a new heading below, one `- [ ]` per finding, with the file
   and line it cited.
3. `bash tests/review-carry.sh` — hand that output to the *same* session as a second
   pass, and ask which earlier findings are fixed, still true, or no longer meaningful.
4. Tick by hand. Only a person ticks a box.

**The rule that keeps this honest.** A finding that survives three reviews has stopped
being a finding and become a decision. Move it into the tracker and tick it here with a
note saying where it went. A log full of ancient open boxes is a log nobody reads.

**A finding is not a verdict.** Reviewers invent concerns when they cannot find real ones.
Record a finding only when the review cited a line. If it made a claim with nothing
traceable behind it, that is worth noting as a failed review rather than as a finding.

---

## Format

    ## 2026-09-06 — 250698b — verdict gap write-up
    - [ ] `flashguard/verify.py:151` coverage reports safe_case_available without a
          reader ever being told what would change it
    - [x] `tests/all.sh:12` soft failure aggregated but exit code not propagated
          — fixed in 141a6f1

---

## 2026-09-07 — 474df9e — the workflow doc reporting itself as a disagreement

Reviewed blind by the CLI, first real use of this workflow. It answered all five questions,
cited lines, and found nothing. Verified independently: the commit is one line in one file
and every description it gave is accurate. An empty review is recorded because a log of only
non-empty reviews is a biased log.

Two things a second pass found that the review did not.

- [x] The review quoted the commit message, which is **not in the packet** — `git diff`
      and `git diff --stat` carry no message and the header prints only the hash. It had a
      shell, ran `git log`, and read the producer's account of the change before answering
      question 1, which asks what changed that was *not* asked for.
      Fixed: the packet now tells the reviewer not to read the commit message, the log, or
      any file explaining why, and `docs/reference/review-workflow.md` says to notice it when
      a review quotes one.
- [x] `tests/check-disputed.sh:22` the commit under review fixed the **document** to get
      past the grep, rather than the grep. The pattern matched the bare word anywhere on any
      line, and already carried two filenames excluded by substring — invisible exemptions,
      the same shape as the publication scan that exempted the only file that could fail it.
      The next document to explain the convention would have hit it again.
      Fixed: a marker is now a line whose first non-space characters are a comment opener and
      then the word. The two skipped paths are skipped by path, for a stated reason, and the
      skip is printed. `review-workflow.md` has its accurate wording back.

Neither is a criticism of the review. The first is the packet's fault and is now the packet's
fix. The second is the kind of thing a blind reviewer is least placed to see, because it
requires asking whether the change was the right shape rather than whether it was correct —
and the commit message it had already read said the change was a fix.

---

*Older reviews go below. Newest at the top.*
