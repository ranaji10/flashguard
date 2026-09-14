# Repair task 2, 14 September. The product is right. The test is not.

**Read this first, because it changes the tone of the work:** the CRLF fix landed and it is
correct. `START-HERE.html:731` and `:768` both normalise `\r\n?` to `\n` before the leak check
and before storing, on both paste paths rather than one. The bare-value fallback is gone, and
the new guard that refuses text with no `ro.x=` shape is better than what was asked for.

The defect is that **the test proving all this cannot fail**, and while it says "ok" it is
hiding a second live defect of the same family.

---

## 1. BLOCKING. Leading whitespace silently zeroes every field. Live now.

Reproduce from the repository root:

```
F=tests/android/real-nothing-phone-2026-08-29.props
grep -v '^#!' $F | bash bench-kit/scripts/derive.sh | grep -E 'partition_scheme|bootloader_state'
grep -v '^#!' $F | sed 's/^/  /' | bash bench-kit/scripts/derive.sh | grep -E 'partition_scheme|bootloader_state'
```

```
canonical           partition_scheme  virtual_A/B   bootloader_state  locked
two leading spaces  partition_scheme  unknown       bootloader_state  unknown
```

Every derived field collapses to `unknown`. The page does not strip per-line whitespace: it
CR-normalises the blob and calls `.trim()`, which touches only the two ends. Indented paste
happens for real — some terminals indent, pasting via a chat window indents, and a phone shell
can indent. The record produced is shaped exactly like the fixture for a phone that answered
nothing.

**Fix:** strip leading and trailing whitespace **per line** in the same normaliser that already
handles CR. One function, one place.

Blank lines are fine: `derive.sh` tolerates them, verified. Do not add handling for a problem
that does not exist.

## 2. BLOCKING. Two of the three shape tests undo their own perturbation.

`tests/test-android-raw-agreement.sh` lines 34-38 and 47-50:

```
crlf_input=$(printf '%s\n' "$bash_raw" | sed 's/$/\r/')
crlf_norm=$(printf '%s\n' "$crlf_input" | tr -d '\r')      # <- undoes it
crlf_derived=$(printf '%s\n' "$crlf_norm" | bash "$DERIVE")
```

It perturbs, un-perturbs, then compares `derive.sh(x)` to `derive.sh(x)`. It is the same
tautology as the line-23 version, in a new costume, and it does not touch the page's normaliser
at all — it reimplements it in bash and tests the reimplementation. The whitespace case at
47-50 has the identical flaw, which is how defect 1 above stayed invisible while the row
printed "ok".

The blind reviewer caught the whitespace one and not the CRLF one. They are the same defect;
finding one instance of a pattern and not the other is worth noticing about the review, not
just about the code.

**The shuffled-key case at lines 59-61 is genuine** — it perturbs and does not undo. Keep it
exactly as it is. It is the model for the rest.

## 3. Test the shipped normaliser, in node. The mechanism already exists.

`tests/run-console-logic.js` extracts logic from `START-HERE.html` by marker comments:

```
/* TESTABLE:name */ ... /* END TESTABLE:name */
```

It was built for a defect in this same family. Use it rather than inventing anything.

**Do this:**

1. In `START-HERE.html`, lift the normalisation into one named function wrapped in those
   markers. It must handle CR and per-line whitespace, and nothing else. Both call sites at 731
   and 768 call it. One implementation, two callers.
2. Extend `tests/run-console-logic.js` (or add a sibling that reuses its extractor) to pull that
   function into node and assert, over every `tests/android/*.props`:
   - canonical text → unchanged
   - CRLF text → normalises to canonical
   - per-line leading and trailing whitespace → normalises to canonical
   - blank lines interleaved → normalises to something `derive.sh` derives identically
   - bare values with no `=` → the page's guard **refuses** it. Test the guard, not the absence
     of a string in the HTML.
3. Rewrite the bash test to do only what bash can do honestly: assert each **un-normalised**
   hazard derives **differently** from canonical. That proves the hazard is real and the
   normaliser is load-bearing. If a hazard ever stops differing, the test should fail and make
   someone ask why, because it means `derive.sh` changed underneath.

Correct the comment at line 9. It currently claims the bare-value fallback is "refused and no
longer offered" while lines 16-22 test only that a string was deleted from the HTML. A comment
that claims coverage the code does not have is the same defect as a run log describing a run
that had not happened.

## 4. Prove each new test fails

For every assertion you add, break the thing it tests, watch it fail with a message that names
the shape, and restore. A test that has never failed is a comment. Both versions of this file
passed continuously while two real defects sat behind them.

---

## Already settled, do not reopen

`tests/webusb-fixtures/18d1-4ee2.desc:10` is Ranaji's ruling and it is recorded in the tracker
under `v-serial`. The fixture contains `<stripped>`, a redaction marker, which is the evidence
the masker ran on the device that caused the fourteen-day leak. Leave the fixture alone.

---

## When you are done

`bash tests/all.sh` at its usual soft exit 2, nothing newly failing, `check-portability.sh`
green under bash 3.2.

Then the part that matters more than the suite: zip `bench-kit/`, unzip somewhere new,
double-click `START-HERE.html`, and run a real phone through the raw-paste path **pasting
deliberately badly** — with indentation, with a blank line in the middle, and once with bare
values. The first two must produce the same record as a clean paste. The third must be refused
with a message that tells the tester what to do instead.

Then `bash tests/handoff.sh` and `bash tests/review-packet.sh` to a fresh reviewing session in
a different model family.
