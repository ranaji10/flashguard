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

## 2026-09-16 — uncommitted-on-3ed8346 — Batch 2b changes on the BenchKit based on MAC vs windows commands

- [ ] tests/run-console-logic.js:157 the schema validation test merely checks whether a string is present in its own hardcoded Set parsed from the Markdown file, instead of testing any actual schema enforcer, meaning the test asserts a tautology and proves nothing about validation.
- [ ] tests/run-console-logic.js:177 the regex /host_shell\s*[:=]\s*"([^"]+)"/g fails to match the ternary assignment cur.host_shell = isCmd ? "cmd" : "powershell" in the application code, allowing the check to pass without actually validating those assigned values.

<details><summary>the review, as it came back</summary>

```
FINDINGS
- [ ] tests/run-console-logic.js:157 the schema validation test merely checks whether a string is present in its own hardcoded Set parsed from the Markdown file, instead of testing any actual schema enforcer, meaning the test asserts a tautology and proves nothing about validation.
- [ ] tests/run-console-logic.js:177 the regex /host_shell\s*[:=]\s*"([^"]+)"/g fails to match the ternary assignment cur.host_shell = isCmd ? "cmd" : "powershell" in the application code, allowing the check to pass without actually validating those assigned values.
```

</details>

---


## 2026-09-16 — uncommitted-on-dba8e8f — Batch 2 changes on the BenchKit based on research

Nothing found. Recorded because a log of only non-empty reviews is a biased log, and because "has this been reviewed at all" is a question worth being able to answer.

<details><summary>the review, as it came back</summary>

```
Based on my review of the diff against the batch 2 requirements, here are the answers to the 5 review questions:

---

1. What changed in the Windows command block?

The Windows quoting bug is fixed by splitting the shell selection and using correct quoting per shell:

- Added scrWindowsShell() (lines 704–723): A new screen asking "Which shell are you using on Windows?" with two buttons — PowerShell and Command Prompt (cmd). The choice is recorded as windows_powershell or windows_cmd.
- Modified scrRoutePlatform() (lines 725–735): The generic "windows" platform now routes to the shell selection screen instead of directly to scrAndroidRaw().
- Modified scrAndroidRaw() (lines 797–843): Now accepts the specific shell platform and generates different quoting:
  - PowerShell → single-quoted: adb shell 'for p in ...; do echo $p=$(getprop $p); done' — PowerShell treats single quotes as literal, so $p and $(getprop $p) pass through to adb unexpanded
  - cmd → double-quoted: adb shell "for p in ...; do echo $p=$(getprop $p); done" — cmd doesn't expand $, so this already worked
- Fixed the heading (line 808): The kicker now shows the actual shell name (PowerShell or Command Prompt (cmd)) instead of the misleading "PowerShell / cmd" label.

---

2. What was decided about the shell split?

Exactly what batch 2 required:
- The Windows branch  paths(windows_powershell and windows_cmd)
- A second question o the tester's actualshell
- Both command blocksies in the same order(line 801) — ro.product.model is preserved
- The answer is recorwnstream knows whichshell produced the capture

---

3. Are the tests correct?

Yes. The test guard in tests/test-android-raw-agreement.sh (lines
16–22) was restored:
if grep -q "adb shell getprop" "$HTML"; then
  echo "  FAIL: STARTprop commands..."
  fail=1
fi
This asserts that no line of START-HERE.html offers a bare adb shell
getprop <key> (which without keys). Theloop forms (for p in ...; do echo $p=$(getprop $p); done) print
key=value and pass. T to catch bare formsbut loose enough not to fire on the loop forms.

---

4. Any phantom features?

No. Only the two files mentioned in batch 2 changed:
- bench-kit/START-HERection + quoting fix
- tests/test-android-raw-agreement.sh — restored the bare-getprop
  guard

No new screens, no neges, no scope creep.The diff is exactly what batch 2 specified.

---

5. Any false-safe paths?

No false-safe introduced. This is Tier A (data collection UI only).
The verifier (flashgud. The fix actuallyremoves a data-corruption path: previously, PowerShell would expand
$p and $(getprop $p)  producing garbageoutput that isValidRawProps would reject — wasting the tester's time
but not entering the aches the device shell correctly on both shells.

---

Summary: The batch 2 work is complete and correct. bash tests/all.sh passes (the false-safverifier corpus,unrelated to this change). The two PowerShell/cmd strings are stated verbatim in the diff
```

</details>

---






## 2026-09-14 — 251df11 — Second Repair run for WebUSB+Benchkit Integration

- [ ] tests/test-android-raw-agreement.sh:5-6 The old test mechanically guarded against
      re-introduction of bare getprART-HERE.html (grepping
      for adb shell getprop ro.product.manufacturer). That assertion was removed. The
      only remaining guard is the p copilot-instructions.md,
      which is a documentation layer, not a mechanical one.

<details><summary>the review, as it came back</summary>

```
Review of 251df11

1. What changed that was not asked for?

I cannot determine this from the diff alone (no rationale was read, by instruction). Everything in the diff forms a coherent unit: extract two functions, use them in both paste paths, test them in Node, and restructure the bash test from "normalised input matches canonical" to "un-normalised input diverges from canonical". Nothing appears orphaned or unrelated.

2. What did it decide that was not already in a file?

The test architecture split — normalisation correctness in Node, hazard existence in bash — is a structural choice. The header comment at tests/test-android-raw-agreement.sh:4-9 documents it after the fact, but no file records why this split was chosen over the prior design (same-suite agreement checks). This is a test strategy decision made in code, not documented as a decision.

3. Does any test pass for a reason other than the code being correct?

No false passes found. Each test exercises the code it claims to. The bare-values test (line 91 of run-console-logic.js) is fragile to a future fixture whose property value contains both = and a substring matching ro.<word>=, but that is a hypothetical: no current fixture has such a value, and the test label accurately describes what happens with the current data.

4. Does any file, name or comment describe something as existing that does not?

Nothing found. The comment at tests/test-android-raw-agreement.sh:8-9 correctly states that tests/run-console-logic.js tests both functions against all fixtures.

5. Does anything here create a path to a false safe?

No. The diff touches bench-kit data collection and tests. It does not modify flashguard/verify.py, any recipe, any corpus file, or the false-safe gate. normaliseRawProps trims whitespace from property lines before they reach derive.sh, which makes derivation more correct,

---

FINDINGS
- [ ] tests/test-android-raw-agreement.sh:5-6 The old test mechanically guarded against
  re-introduction of bare getprART-HERE.html (grepping
  for adb shell getprop ro.product.manufacturer). That assertion was removed. The
  only remaining guard is the p copilot-instructions.md,
  which is a documentation layer, not a mechanical one.
      RECONSTRUCTED 16 September, not rewritten: the text above arrived corrupted mid-line ("bare getprART-HERE.html", "the p copilot-instructions.md"), which is the filer's truncation guard catching a cut-off END but not a cut-out MIDDLE. Left as filed, because a reviewer's words are evidence. What it means: the grep in tests/test-android-raw-agreement.sh that asserted the bare `adb shell getprop <key>` block had not returned to bench-kit/START-HERE.html was removed in the rewrite, leaving only .github/copilot-instructions.md, which is documentation rather than a mechanical guard. STILL OPEN AND CORRECTLY CARRIED. It is the tracker's v-offerguard and it is scheduled in docs/reference/producer-prompt-2026-09-16-batch2.md.
```

</details>

---


## 2026-09-14 — c388c2c — Repair run for WebUSB+Benchkit Integration

- [x] `tests/test-android-raw-agreement.sh:47-50` whitespace/blanks test is a tautology:
      TICKED 16 September, verified against the current file: the whitespace step perturbs with `sed 's/^/  /'` and asserts the derivation DIFFERS from canonical. Nothing strips it back. The tautology went with the c388c2c rewrite.
      adds leading spaces then strips them before asserting, so it tests
      derive.sh(x)==derive.sh(x), not whitespace tolerance; derive.sh
      actually fails on leading-whitespace input (g() requires key at
      position 1)
- [x] `tests/test-android-raw-agreement.sh:8` comment says bare-value fallback "is
      TICKED 16 September, verified: the comment at line 8 now points at tests/run-console-logic.js, which does test bare-value refusal through the shipped isValidRawProps (`bare values with no '=' are refused`, passing on every fixture). The comment and the code agree.
      refused"; lines 16–22 test only that the UI text was removed, not
      that pasting bare values is rejected

<details><summary>the review, as it came back</summary>

```

Review of c388c2c

1. What changed that was not asked for?

Nothing in the diff goes beyond the four files' stated concerns. The changes are: CRLF normalisation, ubuntu_live routing, pending-only records in saveRecord, merge.py gating, schema documentation, and test expansion. No new feature, no new screen, no scope creep.

2. What did it decide that was not already in a file?

Nothing material. The pending-only record shape, the merge.py gate, and the raw validation guard are implementations of constraints that are now documented in data/schema.md:141–146. The ubuntu_live routing change (scrPrep → scrBootUp → scrAndroidBash) is a flow decision that is not documented anywhere as a design choice — but it restores the prep screens that already existed in the code, so it is a routing repair rather than a new decision.

3. Does any test pass for a reason other than the code being correct?

Yes. The whitespace/blanks test at tests/test-android-raw-agreement.sh:47–56 is a tautology. It:

1. Takes clean key=value fixture text (line 31: bash_raw)
2. Adds leading whitespace and blank lines (line 48: awk '{print "  " $0 "\n"}')
3. Strips them back out (line 49: sed 's/^[[:space:]]*//; s/[[:space:]]*$//' | grep -v '^$')
4. Feeds the stripped text to derive.sh
5. Asserts the result matches the original

The normalised text is identical to the original input. The test proves that derive.sh(x) == derive.sh(x), which is determinism, not whitespace robustness. derive.sh cannot handle leading whitespace — its g() function uses index($0, k "=") == 1, which requires the key at position 1. A real whitespace-contaminated paste would silently return unknown for every field.

No code path in the HTML page strips leading whitespace either — the page does rawInput.replace(/\r\n?/g, "\n") and .trim(), neither of which strips per-line leading spaces. So the scenario the test claims to cover (lines 5–8 of the file) would fail in production, but the test passes because it undoes its own perturbation before asserting.

4. Does any file, name or comment describe something as existing that does not?

The test comment at tests/test-android-raw-agreement.sh:8 says it verifies that bare-value fallback "is refused". The test at lines 16–22 checks only that the bare-command UI text was removed from the HTML (a grep -q for its absence). It does not test that pasting bare values into scrAndroidRaw is rejected. The HTML validation at START-HERE.html:769 does reject bare values, so the feature exists — but the test's comment overstates what it proves.

5. Does anything here create a path to a false safe?

No. The changes are on the capture/collection side (bench kit and merge pipeline). The verifier at flashguard/verify.py is not touched. The saveRecord change at START-HERE.html:915–919 reduces what a pending record contains (only android_raw and android_derivation: "pending", no derived fields), which is strictly safer than the previous version that emitted seventeen "unknown" fields alongside the raw text — a record with no partition_scheme field cannot be mistaken for one that was examined. The merge.py gate at lines 101–103 prevents pending records from reaching the published matrix. Neither change touches the verify path.

---

FINDINGS
- [x] `tests/test-android-raw-agreement.sh:47-50` whitespace/blanks test is a tautology:
      TICKED 16 September, verified against the current file: the whitespace step perturbs with `sed 's/^/  /'` and asserts the derivation DIFFERS from canonical. Nothing strips it back. The tautology went with the c388c2c rewrite.
      adds leading spaces then strips them before asserting, so it tests
      derive.sh(x)==derive.sh(x), not whitespace tolerance; derive.sh
      actually fails on leading-whitespace input (g() requires key at
      position 1)
- [x] `tests/test-android-raw-agreement.sh:8` comment says bare-value fallback "is
      TICKED 16 September, verified: the comment at line 8 now points at tests/run-console-logic.js, which does test bare-value refusal through the shipped isValidRawProps (`bare values with no '=' are refused`, passing on every fixture). The comment and the code agree.
      refused"; lines 16–22 test only that the UI text was removed, not
      that pasting bare values is rejected
```

</details>

---


## 2026-09-14 — verification of the five carried findings — not a review

Filed by the analysing session, not by a blind reviewer. It is here because it changes the
severity of two findings and adds evidence neither read had.

**Finding 3 is worse than filed, and it is now reproduced.** The tautological test was
covering a real defect. The two step-2 routes do not differ in derivation, they differ in the
SHAPE of the text that arrives, and `adb shell` on Windows prints CRLF while the raw-paste
path only trims the ends of the blob. Run from the repository root:

```
F=tests/android/real-nothing-phone-2026-08-29.props
grep -v '^#!' $F | bash bench-kit/scripts/derive.sh | grep -E 'partition_scheme|bootloader_state'
grep -v '^#!' $F | sed 's/$/\r/' | bash bench-kit/scripts/derive.sh | grep -E 'partition_scheme|bootloader_state'
```

LF gives `virtual_A/B` and `locked`. CRLF gives `A/B` and `unknown`. The first is a DIFFERENT
CONFIDENT ANSWER on a recipe-matching field, not an abstention. The second throws away an
earned `unsafe`. This affects only the Windows path, which is the platform most testers are
expected to use, and the test written to catch exactly this could not fail.

**The documented cmd.exe fallback produces a meaningless record.** `START-HERE.html:762` tells
a tester to run nineteen bare `adb shell getprop <key>` lines, each printing a value with no
key. `cut -d= -f2- | bash bench-kit/scripts/derive.sh` returns `unknown` for every field, so
the record is shaped exactly like `tests/android/empty-everything.props`, the fixture for a
phone that answered nothing. Following the instructions produces a record indistinguishable
from a dead device.

**Finding 4 is a functional hole, not a stale comment.** `scrPlatform:690` offers the Ubuntu
stick and `scrRoutePlatform:706` routes it straight to `scrAndroidBash("linux_live")`. A
tester who picks it is told to run a bash script on a machine nobody told them how to make.

**Finding 5's severity is as the reviewer's long note stated**, and that note was right: no
false safe today because the verifier abstains on `unknown`, but seventeen fields claiming
"could not be established read-only" when they mean "not computed yet" pollutes the matrix the
first moment anything treats `unknown` as ground truth. Nothing outside START-HERE.html knows
these fields exist, which is how it stays latent.

**Finding 1 is a wording defect in the finding, not a defect in the fixture.** The fixture
contains `<stripped>`, a redaction marker, which is the evidence the masker ran on the device
that caused the fourteen-day leak. Removing it would remove the proof. Ranaji's ruling.

Repair task: `docs/reference/producer-prompt-2026-09-14-repair.md`.

---


## 2026-09-14 — d83c342 — Integration of WebUSB and Bench Kit for a tool that can be run by independent testers

- [x] tests/test-android-raw-agreement.sh:23 Route 2 sets raw_paste="$bash_raw" — the same variable Route 1 used — then pipes it through the same derive.sh. The test compares identical input through identical processing and always passes regardless of code correctness.
      TICKED 16 September, verified against the current file: test-android-raw-agreement.sh was rewritten end to end in c388c2c. Line 23 is now the canonical baseline `bash_derived=$(printf ... | bash $DERIVE)`, and `grep -n 'tr -d'` over the whole file returns nothing. Every hazard step perturbs and does NOT undo.
- [x] bench-kit/START-HERE.html:784 Comment says "Legacy Ubuntu Prep & Boot Screens (Accessible if requested)" but no calling path in the file reaches scrPrep() or scrBootUp(). The functions are dead code; the comment describes reachability that does not exist.
      TICKED 16 September, verified: the string `Legacy` does not appear anywhere in bench-kit/START-HERE.html, and `git log -S` shows c388c2c removed that comment on 14 September. The reachability claim is also false now: scrRoutePlatform reaches scrPrep, and scrPrep reaches scrBootUp.
- [x] bench-kit/START-HERE.html:914 android_raw and android_derivation are not in the schema (data/schema.md). The raw-paste path writes an undocumented field to the record and marks 17 Android fields as "unknown" meaning "not yet derived", conflating it with "unknown" meaning "could not be established read-only" — the exact ambiguity schema version 0.2 was redesigned to eliminate.
      TICKED 16 September. Fixed in batch 1: data/schema.md documents android_raw and android_derivation as a distinct uncomputed state, buildAndroidBlock emits exactly those two keys for a raw capture, data/merge.py refuses a pending record, and tests/test_contributions_validation.py fails when that refusal is removed (verified by planting `if False:`).

<details><summary>the review, as it came back</summary>

```
Review of d83c342

1. What changed that was not asked for?

The commit title says "Integrate WebUSB step 1 and multi-platform step 2 into START-HERE.html". Beyond that integration:

- tests/webusb-probe.html received a four-line SUPERSEDED notice (lines 1–4). This is commentary on a file the diff does not modify substantively and was not part of the stated scope, though it is harmless.
- The legacy Ubuntu screens (scrPrep, scrBootUp) were gutted to stubs (lines 784–807). The diff removed detailed preparation and boot guides that existed in v3 and replaced them with skeleton cards. No calling path reaches them (covered under Q4), so this is dead code added rather than retained. It could have been removed entirely; leaving it creates the appearance of functionality that does not exist.

2. What did it decide that was not already in a file?

- capture_route defaults to "browser" on every new capture (bench-kit/START-HERE.html:437). The schema doc (data/schema.md:152–153) says capture_route was added to distinguish what the shipped tool can do from what linux_live can do, and warns "absence is not a value; an unrecorded capture must not be assumed to have used any particular route." The HTML picks "browser" as the default before knowing whether WebUSB succeeded, whether the user skipped it, or whether the tester went through the bash path. The bash path later overwrites it to "adb_host" (line 776), and the raw-paste path sets "adb_host" too — so the default only survives for non-phone devices that go through scrWebUSB and reach scrConfirm. That default itself is reasonable (WebUSB is the browser route), but the decision to make "browser" the fallback rather than "not_stated" or a sentinel for "undetermined" was made in this commit, not derived from any prior document.
- android_derivation: "pending" as a record field (line 915). The raw-paste path stores the tester's pasted text as android_raw and marks derivation as "pending", meaning the record is written with all Android fields set to "unknown" and derivation deferred. No document I was told to read specifies this deferred-derivation pattern. The schema (data/schema.md) has no android_raw or android_derivation field. The record will be written to device-matrix.jsonl with an undocumented field and a batch of "unknown" values that mean "not yet derived" rather than "could not be established read-only" — conflating two of the three-way absence semantics the schema was specifically redesigned to distinguish (schema.md lines 37–43).

3. Does any test pass for a reason other than the code being correct?

Yes. tests/test-android-raw-agreement.sh is a tautology.

The test claims to assert that "the bash path (02-android.sh) and the raw-paste path produce the same derived fields when derive.sh runs over the raw property text."

Lines 18–24:

# Route 1: Simulated bash path (derived directly)
bash_raw=$(grep -v '^#!' "$f")
bash_derived=$(printf '%s\n' "$bash_raw" | bash "$DERIVE")

# Route 2: Simulated raw paste path (verbatim raw text, derived via derive.sh)
raw_paste="$bash_raw"
raw_derived=$(printf '%s\n' "$raw_paste" | bash "$DERIVE")

Route 2 sets raw_paste="$bash_raw" — the identical variable from Route 1 — and pipes it through the identical command (bash "$DERIVE"). The comparison at line 26 ("$bash_derived" = "$raw_derived") compares two runs of the same function on the same input. It will always pass.

The test the name promises — that the raw-paste path in START-HERE.html and the bash path through 02-android.sh produce the same record — would require either (a) actually exercising the raw-paste parsing code to produce key=value lines, or (b) at minimum, transforming the fixture text differently for each route. As written, Route 2 is Route 1 copy-pasted with a different variable name.

This test is wired into tests/all.sh (the line echo "  ANDROID RAW AGREEMENT"; bash "$HERE/test-android-raw-agreement.sh" || exit 1), so it runs in the build and reports "ok" across all fixtures, giving the appearance of coverage where none exists.

4. Does any file, name or comment describe something as existing that does not?

Yes. bench-kit/START-HERE.html:784:

/* ---------- Legacy Ubuntu Prep & Boot Screens (Accessible if requested) ---------- */

scrPrep() and scrBootUp() are defined at lines 785–807. The comment says they are "Accessible if requested." They are not accessible: no button, no event handler, and no initialization code in the file calls either function. The v3 flow that reached them (the location chooser scrBoot, then the setup script step scrSetup) was removed in this diff. The functions are dead code, and the comment claims they are reachable.

5. Does anything here create a path to a false safe?

Not directly. The else if (cur.dev.expect) devClass = cur.dev.expect; fallback at line 639 echoes the tester's category selection as the detected device class when no interface-level match fires, which means a misidentified device category could propagate to the record as device_class. But device_class on the record flows into the device matrix, not into the verifier's verdict path — the verifier takes a fingerprint and a recipe as input, not a bench-console device class. This fallback affects data quality, but it does not create a code path where verify.py returns safe when it should not.

The android_raw / android_derivation: "pending" pattern (lines 912–923) writes every Android field as "unknown", which the verifier should treat as an abstention signal. As long as the verifier continues to abstain on unknown fields — which it does; the build fails on a false safe, and the suite output confirms the false-safe gate is armed — this does not produce a false safe. But it is worth noting that a record carrying 17 "unknown" Android fields is not the same as a record with "unknown" because the device did not expose the properties: the former will be derived later, the latter is final. If a future merge.py or coverage.py change treats every "unknown" as ground truth, these deferred-derivation records would silently pollute the matrix.

---

FINDINGS

- [x] tests/test-android-raw-agreement.sh:23 Route 2 sets raw_paste="$bash_raw" — the same variable Route 1 used — then pipes it through the same derive.sh. The test compares identical input through identical processing and always passes regardless of code correctness.
      TICKED 16 September, verified against the current file: test-android-raw-agreement.sh was rewritten end to end in c388c2c. Line 23 is now the canonical baseline `bash_derived=$(printf ... | bash $DERIVE)`, and `grep -n 'tr -d'` over the whole file returns nothing. Every hazard step perturbs and does NOT undo.
- [x] bench-kit/START-HERE.html:784 Comment says "Legacy Ubuntu Prep & Boot Screens (Accessible if requested)" but no calling path in the file reaches scrPrep() or scrBootUp(). The functions are dead code; the comment describes reachability that does not exist.
      TICKED 16 September, verified: the string `Legacy` does not appear anywhere in bench-kit/START-HERE.html, and `git log -S` shows c388c2c removed that comment on 14 September. The reachability claim is also false now: scrRoutePlatform reaches scrPrep, and scrPrep reaches scrBootUp.
- [x] bench-kit/START-HERE.html:914 android_raw and android_derivation are not in the schema (data/schema.md). The raw-paste path writes an undocumented field to the record and marks 17 Android fields as "unknown" meaning "not yet derived", conflating it with "unknown" meaning "could not be established read-only" — the exact ambiguity schema version 0.2 was redesigned to eliminate.
      TICKED 16 September. Fixed in batch 1: data/schema.md documents android_raw and android_derivation as a distinct uncomputed state, buildAndroidBlock emits exactly those two keys for a raw capture, data/merge.py refuses a pending record, and tests/test_contributions_validation.py fails when that refusal is removed (verified by planting `if False:`).
```

</details>

---


## 2026-09-13 — edb6008 — Restoring missed findings

- [x] tests/webusb-fixtures/18d1-4ee2.desc:10 stores a device serial number (_SN:<stripped>)
      TICKED 16 September, ruled 14 September and never recorded here, which is why it came back five times. The fixture contains `<stripped>`, the redaction MARKER, not a serial -- the finding quotes the marker in its own text. It is the evidence the masker ran on the device that caused the fourteen-day leak, and removing it would remove the proof.
      in the product field, violating the strict data rule against recording serials.
- [x] tests/webusb-probe.html:94 removes the protective comment explaining why **Fixed and confirmed by the second read, 14 Sep: the comment is restored at lines 96-103 with the masker beside it.**
      serial numbers are not read or printed, an unasked-for change that enabled the leak above.

<details><summary>the review, as it came back</summary>

```
1. What changed that was not asked for?
N/A
2. What did it decide that was not already in a file?
N/A
3. Does any test pass for a reason other than the code being correct?
N/A
4. Does any file, name or comment describe something as existing that does not?
N/A
5. Does anything here create a path to a false safe?
N/A

  FINDINGS
  - [x] tests/webusb-fixtures/18d1-4ee2.desc:10 stores a device serial number (_SN:<stripped>)
      TICKED 16 September, ruled 14 September and never recorded here, which is why it came back five times. The fixture contains `<stripped>`, the redaction MARKER, not a serial -- the finding quotes the marker in its own text. It is the evidence the masker ran on the device that caused the fourteen-day leak, and removing it would remove the proof.
        in the product field, violating the strict data rule against recording serials.
  - [ ] tests/webusb-probe.html:94 removes the protective comment explaining why
        serial numbers are not read or printed, an unasked-for change that enabled the leak above.
```

</details>

---


## 2026-09-13 — b73c93f — Variant Grading and v0.2 tests

- [x] `docs/reasoning/safe-case.md:39`
      AUTHORISED, and the reviewer could not have known. Both decisions were made by Ranaji on
      12 Sep and relayed in the task; the resolution in safe-case.md matches them word for word.
      The packet deliberately excludes the task, so a blind reviewer flags every authorised
      decision as unauthorised. That is a permanent cost of blindness, not a defect, and it is
      cheaper than the alternative. Noted here so the next one is recognised quickly.
- [x] `flashguard/verify.py:282`
      REAL, AND BIGGER THAN IT LOOKED. identity_source is not invented: it is a schema field
      carried by 8 of the 10 records in the matrix, set whenever a tester names the DEVICE. Read
      as variant confirmation, almost every real record would have confirmed its own variant
      with no human involved. variant_source and human_confirmed were genuinely invented.
      Fixed: one field, variant_confirmed_by, defined in data/schema.md, absence means no
      confirmation. Test added asserting tester_identified does NOT confirm a variant.
- [x] `docs/reasoning/verdict-contract.md:75`
      REAL. The contract listed four prerequisite fields; the verifier reads the key and
      `required` only. Fixed in the contract rather than the code: declared_by and
      source_evidence are provenance and legitimately unread, but a contract that lists four
      fields without distinguishing them implies all four participate. `state` is carried and
      unread on every recipe and should be dropped if it stays that way.
- [x] `tests/test_verify_v2.py:131`
      REAL. Fixed in cf1b009: a test that enters the dangerous branch now exists and fails on
      the old code.
- [x] `flashguard/verify.py:276`
      REAL, AND IT WAS A SHIPPED FALSE SAFE. Reproduced against the FP3 recipe before changing
      anything: alias device code, unknown variant, prerequisite satisfied, verdict safe, zero
      variant reasons, and fields_consumed still claiming the variant. Fixed in cf1b009: an
      unconfirmed variant always abstains, and whether supported_device_codes is a variant- or
      family-level claim is now DISPUTED rather than decided by a branch.

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
- [x] `docs/reasoning/safe-case.md:39`
      AUTHORISED, and the reviewer could not have known. Both decisions were made by Ranaji on
      12 Sep and relayed in the task; the resolution in safe-case.md matches them word for word.
      The packet deliberately excludes the task, so a blind reviewer flags every authorised
      decision as unauthorised. That is a permanent cost of blindness, not a defect, and it is
      cheaper than the alternative. Noted here so the next one is recognised quickly.
- [x] `flashguard/verify.py:282`
      REAL, AND BIGGER THAN IT LOOKED. identity_source is not invented: it is a schema field
      carried by 8 of the 10 records in the matrix, set whenever a tester names the DEVICE. Read
      as variant confirmation, almost every real record would have confirmed its own variant
      with no human involved. variant_source and human_confirmed were genuinely invented.
      Fixed: one field, variant_confirmed_by, defined in data/schema.md, absence means no
      confirmation. Test added asserting tester_identified does NOT confirm a variant.
- [x] `docs/reasoning/verdict-contract.md:75`
      REAL. The contract listed four prerequisite fields; the verifier reads the key and
      `required` only. Fixed in the contract rather than the code: declared_by and
      source_evidence are provenance and legitimately unread, but a contract that lists four
      fields without distinguishing them implies all four participate. `state` is carried and
      unread on every recipe and should be dropped if it stays that way.
- [x] `tests/test_verify_v2.py:131`
      REAL. Fixed in cf1b009: a test that enters the dangerous branch now exists and fails on
      the old code.
- [x] `flashguard/verify.py:276`
      REAL, AND IT WAS A SHIPPED FALSE SAFE. Reproduced against the FP3 recipe before changing
      anything: alias device code, unknown variant, prerequisite satisfied, verdict safe, zero
      variant reasons, and fields_consumed still claiming the variant. Fixed in cf1b009: an
      unconfirmed variant always abstains, and whether supported_device_codes is a variant- or
      family-level claim is now DISPUTED rather than decided by a branch.
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
