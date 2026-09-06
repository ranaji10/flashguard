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

*No reviews recorded yet. The first one goes above this line, newest at the top.*
