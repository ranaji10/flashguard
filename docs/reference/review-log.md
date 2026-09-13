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

## 2026-09-13 — b73c93f — Variant Grading and v0.2 tests

- [ ] docs/reasoning/safe-case.md:39 it resolved two DISPUTED blocks on variant
      matching and expiry that explicitly require
- [ ] flashguard/verify.py:282 it invented specific fingerprint keys and values to
      represent human variant confirmation which le
- [ ] docs/reasoning/verdict-contract.md:75 it states prerequisites carry state,
      declared_by, etc. but the verifier code comds
- [ ] tests/test_verify_v2.py:131 the test for an unconfirmed variant passes only
      because its recipe's supported_device_codes
- [ ] flashguard/verify.py:276 bypassing the missing-variant abstain reason when
      observed_device matches an alias creates a

<details><summary>the review, as it came back</summary>

```
1. What changed that was not asked for?
   The assistant resolved the two DISPUTED blocks regarding variant matching and the evidence expiry boundary (around docs/reasoning/safe-case.md:39). It decided them itself and removed the markers, despite those markers explicitly stating that no test could settle them and that they "need a decision from Ranaji".
2. What did it decide that was not already in a file?
   It decided on specific fingerprint keys (variant_source, identity_source, human_confirmed) and strings ("human", "tester_identified", "human_confirmed") to evaluate whether a variant was human-confirmed (flashguard/verify.py:282). These mapping decisions and keys were invented in this commit and were not defined in the contract or any other file prior.
3. Does any test pass for a reason other than the code being correct?
   Yes. In tests/test_verify_v2.py:131, test_unconfirmed_variant_with_agreeing_partition_and_bootloader_abstains_naming_variant asserts that an unconfirmed variant results in a cannot-verify verdict. This test only passes because BASE_RECIPE leaves supported_device_codes empty. Because of a bug in the code, if product_device matched an alias, it would wrongly skip the abstain altogether.
4. Does any file, name or comment describe something as existing that does not?
   Yes. docs/reasoning/verdict-contract.md:75 describes prerequisites as carrying state, declared_by, and source_evidence. However, the verification code (flashguard/verify.py:336-339) ignores all of these fields entirely and only retrieves the required field, making the contract's description of the structure an unfulfilled claim.
5. Does anything here create a path to a fals
   Yes. At flashguard/verify.py:276, if a recipe requires a variant but the fingerprint does not provide one (it is unconfirmed), the code explicitly passes—s-variant abstain reason—if the observed_device happens to match a supported_device_codes alias. This directly violates the contract (which states an unconfirmed
   variant must return cannot-verify and NEVEr path to a false safe.

  FINDINGS
- [ ] docs/reasoning/safe-case.md:39 it resolved two DISPUTED blocks on variant
  matching and expiry that explicitly require
- [ ] flashguard/verify.py:282 it invented specific fingerprint keys and values to
  represent human variant confirmation which le
- [ ] docs/reasoning/verdict-contract.md:75 it states prerequisites carry state,
  declared_by, etc. but the verifier code comds
- [ ] tests/test_verify_v2.py:131 the test for an unconfirmed variant passes only
  because its recipe's supported_device_codes
- [ ] flashguard/verify.py:276 bypassing the missing-variant abstain reason when
  observed_device matches an alias creates a
```

</details>

---


## 2026-09-08 — 0e2041d — double checking before verifier build

- [x] `tests/review-log-add.sh:43` decided whether a review covered uncommitted
      work by matching the substring "uncommitted" inside a human sentence, so an
      explicit BASE like `fix-uncommitted-bug` would have filed committed work as
      uncommitted. Fixed in c85da82: the packet writes a MODE token as its own
      field, so nothing has to infer the mode from prose.
      (This finding also arrived truncated, the second in a row. cad6129 now
      catches a line number running into mid-word text, which is that
      failure's signature.)

<details><summary>the review, as it came back</summary>

```
Good. Now I have what I need to answer the five questions about commit 0e2041d.

---

1. What changed that was not asked for?

The two trailing-newline additions in data/recipe_format_coverage.py:119 and docs/reasoning/recipe-format-coverage.md:143 are cosmetic whitespace fixes — not substantive, not harmful, and not on any verification path. Whether they were asked for is unknowable from the diff; either way, they change nothing that matters.

The remaining three files — docs/reference/review-log.md, tests/review-log-add.sh, and tests/review-packet.sh — all address one thing: the filing process was stamping reviews against the wrong commit. That is a single fix across three files. Nothing in the diff introduces a feature, a concept, or a capability beyond correcting the logging plumbing.

2. What did it decide that was
                                                                                          One decision is made: review-paence file(.git/review-packet-ref) and review-log-add.sh reads it to determine the SHA for the      heading. This decision is documsts/review-packet.sh:38–43 andtests/review-log-add.sh:36–38, and the VOID header in docs/reference/review-log.md:56–63  records why.
                                                                                          The pipe-delimited format (WHERreview-packet.sh:44 is notdocumented anywhere as a contract — it exists only implicitly, coupled between the printf at line 44 and the cut at testss is fine for two scripts in thesame directory, but it is a decision that lives only in code, not in prose.               
3. Does any test pass for a reason other than the code being correct?                     
The new logic has a fallback: when no review-packet-ref file exists, review-log-add.sh:48 falls back to $(git log -1 --foing. This means the old behaviour is preserved as a degraded path — existing tests that never build a packet first still work. That is correct rather th tells the user the heading mayname the wrong thing.

The case match at review-log-add.sh:43–46 tests $W for *uncommitted*. The packet writes
WHERE as the first field (tests WHERE is set to "uncommittedwork in the tree" at line 33. The glob *uncommitted* matches this. However, it would also
match any explicit BASE argumento contain the substring"uncommitted" — e.g., a branch named fix-uncommitted-bug would produce WHERE="explicit
range fix-uncommitted-bug..HEADted*, and the SHA would bewritten as uncommitted-on-<hash> when it should not be. This is not a test-correctness
issue per se, but it is a fragi

4. Does any file, name or commexisting that does not?

The VOID entry at docs/referenc

▎ Fixed: review-packet.sh now wgit/review-packet-ref, andreview-log-add.sh files against that rather than assuming HEAD.

This describes the fix as already done, and the code confirms it does exist (review-packet.sh:44–45, reviewstale descriptions found.

5. Does anything here create a

No. None of these files are on ipe_format_coverage.py is ameasurement script. recipe-format-coverage.md is a reasoning document. The three
review-tooling files are test iand label reviews. Nothing inthis diff touches flashguard/verify.py, the verdict contract, any recipe, or any schema.

---

FINDINGS
- [ ] tests/review-log-add.sh:4atches on substring, so a branch
  name or explicit BASE containing "uncommitted" (e.g. fix-uncommitted-bug) would
  produce a uncommitted-on- SHAreviewed committed work
```

</details>

---


## 2026-09-08 — 999ad74 — before the verifier build

**VOID. This did not review 999ad74.** The packet was built while two trailing-newline
edits were uncommitted, so it diffed those two characters and nothing else, and the filer
stamped it with the last commit hash. The 269-line coverage measurement in 999ad74 has
never been reviewed. Kept rather than deleted, because a log that quietly loses its own
mistakes is not a record.

Fixed: `review-packet.sh` now writes what it covered to `.git/review-packet-ref`, and
`review-log-add.sh` files against that rather than assuming HEAD.

Nothing found. Recorded because a log of only non-empty reviews is a biased log, and because "has this been reviewed at all" is a question worth being able to answer.

<details><summary>the review, as it came back</summary>

```
The diff is clear: both files had their final line missing a trailing newline, and the only change is adding that trailing newline. Let me confirm there's nothing else by checking what the review packet's "1 OPEN DISAGREEMENT" and "PLACEHOLDERS" refer to, since those are suite outputs not part of my review scope.

The diff is two files, each with a single-character change: a missing newline at end-of-file is added. That's the entire content.

1. What changed that was not asked for?

Nothing substantive changed. Both edits add a trailing newline to the final line of the file — data/recipe_format_coverage.py:119 and docs/reasoning/recipe-format-coverage.md:143. No logic, no prose, no data was altered. Whether this was asked for or not, it changes nothing that matters.

2. What did it decide that was not already in a file?

Nothing. No decision is expressed in either edit.

3. Does any test pass for a reaing correct?

Not from this diff. The change ng newline). It cannot affecttest outcomes in either direction.

4. Does any file, name or comment describe something as existing that does not?

No. The content of both files is unchanged except for the newline character.

5. Does anything here create a path to a false safe?

No. Neither file is on the verification path. recipe_format_coverage.py is a measurement
script; recipe-format-coverage.. Neither touchesflashguard/verify.py or any verdict logic.

---

FINDINGS
none
```

</details>

---


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
