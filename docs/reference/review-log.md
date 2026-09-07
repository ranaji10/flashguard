# Review log

*What each blind review found, and whether it was ever fixed.*

**Why this exists.** `tests/review-packet.sh` hands a reviewer a diff and nothing else, so
that it reads the work rather than the producer's account of it. That blindness is right
for finding defects and useless for tracking them: every review began and ended in the
same session, and a finding nobody acted on simply vanished. This file is the memory the
reviewer is deliberately denied.

**How to use it.** Five commands, two pastes, and nothing to retype.

1. `bash tests/review-packet.sh | pbcopy` — paste into a fresh session as the first
   and only message. No summary, no context. Let it answer.
2. Copy its whole answer. It ends with a paste-ready block, because the packet asks for
   one — filing a review must not mean reading five paragraphs and hand-writing
   checkboxes from them, or it becomes the step that gets skipped.
3. `pbpaste | bash tests/review-log-add.sh "short label"` — files it here with the
   right heading and today's date, keeps the full answer in a collapsed block, and
   refuses a ticked box.
4. `bash tests/review-carry.sh | pbcopy` — paste into the **same** session as a second
   pass, and it says which earlier findings are fixed, still true, or no longer meaningful.
5. Tick by hand, then commit. Only a person ticks a box.

**The rule that keeps this honest.** A finding that survives three reviews has stopped
being a finding and become a decision. Move it into the tracker and tick it here with a
note saying where it went. A log full of ancient open boxes is a log nobody reads.

**A finding is not a verdict.** Reviewers invent concerns when they cannot find real ones.
Record a finding only when the review cited a line. If it made a claim with nothing
traceable behind it, that is worth noting as a failed review rather than as a finding.

---

## Format

Written by `tests/review-log-add.sh`, so this is what it produces rather than what anyone
has to remember:

    ## 2026-09-06 — 250698b — verdict gap write-up
    - [ ] `flashguard/verify.py:151` coverage reports safe_case_available without a
          reader ever being told what would change it
    - [x] `tests/all.sh:12` soft failure aggregated but exit code not propagated
          — fixed in 141a6f1

Each entry keeps the reviewer's whole answer underneath in a collapsed block, so "was this
actually reviewed" stays answerable. `review-carry.sh` skips fenced blocks, so a finding
quoted inside the stored answer is not counted a second time.

---

<!-- NEWEST REVIEW DIRECTLY BELOW -->

## 2026-09-07 — 047af5a — recipes indeed have prerequisites

- [x] `tests/tracker-export.py:60` the `fingerprint()` docstring still said the hash
      covers "the lengths of the body and note" while the code hashes the content. It
      described the behaviour this commit removed. Fixed 7 Sep.

**This entry arrived corrupted, and that is worth keeping rather than tidying away.** The
stored answer below is missing runs of characters ("or commexisting that does not", "a
versiohe project tracker"), and the finding line was unreadable as filed. The clipboard was
copied while the CLI was still rendering, so `pbpaste` took a partly-written buffer. The
finding itself was correct and has been rewritten above from the readable fragments.
`tests/review-log-add.sh` now refuses input that looks truncated, because a finding nobody
can read is carried forward for ever and can never be honestly ticked.

<details><summary>the review, as it came back</summary>

```
Here is my review.

Answers

1. What changed that was not asked for?

Nothing. Both files contain the same change: the fingerprint string now includes the full body and note content instead of their lengths, and the hash iterates UTF-16 code units instead of Python ord() on characters. The JS page (not version-controlled) already carries the matching update. The scope is tight.

2. What did it decide that was not already in a file?

Nothing new was decided. The fingerprint's purpose (detect drift between file and published page) and the hash algorithm (djb2) are unchanged. The implementation was corrected, not redesigned.

3. Does any test pass for a reason other than the code being correct?

No. check-tracker.sh computes the fingerprint independently from tracker-export.py (one parses the HTML inline, the other is a standalone script), and both must agree with the JavaScript page for the version banner to match. The hash is computed against real tracker data, not a stub.

4. Does any file, name or commexisting that does not?

Yes. tests/tracker-export.py:60cstring says the hash covers "the lengths of the body and note". The code on lines 68–69 now hashes the bodies themselves.
The docstring describes the oldat this commit replaced.

5. Does anything here create a

No. The fingerprint is a versiohe project tracker. It has noconnection to flashguard/verify.py or the verdict logic.

---

FINDINGS
- [ ] tests/tracker-export.py:6ths of the body and note" but the
  code now hashes the full content, not lengths; it describes the pre-fix behavior
  that this commit removed
```

</details>

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
