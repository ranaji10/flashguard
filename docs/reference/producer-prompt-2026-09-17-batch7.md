# Batch 7: the last build before testing

**Objective.** When this batch is committed, nothing else gets built before the hackerspace
evening on 22 September or the remote wave. The verifier is final for the testing
programme, the tester package can be built by one command, a returned session can be
brought into the matrix by one command, and there is a runbook for the evening.

After this batch the rule changes: **only defects found by testers get fixed**, and every
fix re-runs the full suite. No new features, no new fields, no refactors.

Three parts, in order. **Stop at the first part whose paste-back fails** and say which
command failed. Commit after each part on its own, so a later part can be reverted without
losing an earlier one.

## Ground rules for every section

- The suite is `bash tests/all.sh`. **pytest is not installed on this machine.** Do not
  write paste-back commands that use it. Unit tests run with `python3 tests/<file>.py`.
- Do not change `data/device-matrix.jsonl` or anything in `data/contributions/` by hand.
  They are captured evidence.
- Do not touch `docs/tracker/` or anything under `library/`.
- Do not widen a gate to make a test pass. If a test and a gate disagree, say which and stop.
- Do not add a second name for anything. Every section below that removes a name removes it
  everywhere, including comments and docs.
- `verify()` stays a pure function: no device I/O, no network, deterministic given its two
  arguments. Reading a data file once at import is allowed, as `guidance.py` already does.
- Never run anything on the never-run list in `CLAUDE.md`. Nothing in this batch needs a device.

---

# PART A: the verifier, final for testing

## A1. Every write must declare its unlock (tracker: v-opsblind)

### Reproduce first

```
python3 - <<'PY'
import json, copy, sys; sys.path.insert(0, '.')
from flashguard.verify import verify
base = json.load(open('data/recipes-v0.2/spacewar.json'))
fp = {"product_device": "Spacewar", "product_model": "A063", "partition_scheme": "virtual_A/B"}
r = copy.deepcopy(base); p = r['prerequisites'].pop('bootloader_state')
p.pop('unlock_class'); p.pop('unlock_step'); p['declared_by'] = 'fastboot_flashing'
r['prerequisites']['oem_status'] = p
print("unlock renamed, no marker ->", verify(dict(fp, oem_status="unlocked"), r)['verdict'])
r = copy.deepcopy(base)
r['prerequisites'] = {"android_version": {"state": "OPEN", "required": 12, "declared_by": "requirements.android"}}
r['operations'] = [{"kind": "write-image", "partition": "boot"}]
print("write-image, no unlock prerequisite ->", verify(dict(fp, android_version=12), r)['verdict'])
PY
```

Expected today: `safe` twice. If not, stop and say so.

### What to change

1. **Declare the operation vocabulary in data, once.** Create `data/vocabulary.json`:

   ```json
   {
     "operation_kinds": {
       "write-image":       {"requires_unlock": true},
       "boot-recovery":     {"requires_unlock": true},
       "unlock_bootloader": {"requires_unlock": true},
       "unlock":            {"requires_unlock": true}
     },
     "unlock_classes": ["command", "out_of_band"],
     "refused_prerequisite_names": {"bootloader_unlocked": "bootloader_state"},
     "prerequisite_comparisons": ["equal", "exact_major", "minimum"]
   }
   ```

   Load it once at import in `flashguard/verify.py`, the same way `guidance.py` loads its file.
   `data/schema.md` gets a section that names `data/vocabulary.json` as the only declaration
   and repeats its contents in a table; a test asserts the table and the JSON agree exactly.

2. **Invert on operations.** In `_verify_v2`, before the prerequisite loop:
   - `operations` absent, null or empty: abstain `operations-none-declared`. Same reasoning as
     `prerequisites-none-declared`: v0.2 has no proof the procedure does nothing.
   - Any operation whose `kind` is not in `operation_kinds`: abstain
     `operation-kind-unrecognized`, naming the kind. **Unknown kinds abstain.** The safe
     direction is the narrow one.
   - Any operation with `requires_unlock: true`, and no prerequisite carrying an `unlock_class`
     from `unlock_classes`: abstain `unlock-undeclared-for-operation`, naming the operation.

   Delete `has_unlock_operation` and the `unmarked-unlock-step` code. The new check replaces
   both. Update every test and document that names `unmarked-unlock-step`.

3. **Keep the prerequisite-side abstention, and move its names into data.** A prerequisite
   still counts as an unlock step when it carries `unlock_step: true` or `unlock_class`, or when
   its `declared_by` contains `unlock`. The hard-coded tuple
   `("bootloader_unlocked", "bootloader_state")` goes. The unlock condition field is whatever
   prerequisite carries an `unlock_class`. Do not add a replacement list.

### Tests this section must add

- The two recipes from the reproduction above: both `cannot-verify` on
  `unlock-undeclared-for-operation`, since neither prerequisite carries an `unlock_class`.
- `write-image` with only an `android_version` prerequisite: `unlock-undeclared-for-operation`.
- An operation kind `flash-everything`: `operation-kind-unrecognized`.
- `operations: []`: `operations-none-declared`.
- The schema table and `data/vocabulary.json` agree.

## A2. One meaning for prerequisite names (tracker: v-unlockkey)

The mapping table in `data/schema.md` currently means "this recipe name is fine, the evidence
lives in that field". The verifier ignores it and reads the recipe name off the fingerprint.
The check resolves through it. So the check approves `bootloader_unlocked`, which the verifier
cannot answer. Pick one meaning: **a prerequisite is named by the fingerprint field itself.**

1. `verify()`: a prerequisite whose name is a key of `refused_prerequisite_names` abstains with
   `prerequisite-name-refused`, and the message names the field to use instead.
2. `tests/test_verify_v2.py` producibility check: resolve nothing through a mapping. A
   prerequisite key must be a field `bench-kit/scripts/derive.sh` emits. A refused name fails
   with a message naming the recipe, the refused name and its replacement.
3. Replace the mapping table in `data/schema.md` with the section from A1.
4. Move the producibility check out of the unit test file into `tests/check-recipes.py`, run
   from `tests/all.sh` under a `RECIPES` heading, exit 1 on failure. It is a build check, and
   the batch 6 reviewer read it as an out-of-scope test because of where it lived.

### Test this section must add

Plant the defect that started this: a copy of spacewar.json with its prerequisite renamed back
to `bootloader_unlocked`. The check must fail on it, **and** `verify()` must return
`cannot-verify` with `prerequisite-name-refused`. Both, in one test.

## A3. Version comparison is declared, never guessed (tracker: v-versionrule)

**Ruling, and why it is not "minimum".** Both upstream sources in this corpus mean an exact
version, in their own words:

- OpenAndroidInstaller, `requirements_view.py`, for `requirements.android`: *"If your current
  installation is newer or older than Android 12, please upgrade or downgrade to the required
  version before proceeding."*
- LineageOS `spacewar.yml`, `before_install: needs_specific_android_fw, version: '15'`, rendered
  as *"LineageOS builds for this device require an Android 15 version of the stock OS"*.

Treating these as minimums would let a recipe with a classified unlock return `safe` for a
phone on Android 13 while the upstream installer tells that user to downgrade first. That is a false safe, so the comparison must
come from the recipe's source, not from the field name.

### What to change

1. Every prerequisite whose `required` is numeric, or a string that parses as a version, must
   carry `"compare"`: one of `prerequisite_comparisons`.
   - `equal`: exact equality after normalisation (categorical fields like `bootloader_state`
     use this; it is also the default when `required` is a non-numeric string and `compare` is
     absent).
   - `exact_major`: the leading integer of observed equals the leading integer of required.
     `"15"`, `15`, `"15.0.2"` all have major 15.
   - `minimum`: observed version tuple is at least required version tuple.
2. A numeric or version `required` with no `compare`: abstain
   `prerequisite-<name>-comparison-undeclared`. Never pick one.
3. Parse both sides. The real Nothing Phone capture carries `android_version: "15"` as a
   **string**; recipes carry `12` as an integer. Today `"12" != 12` returns `unsafe` on a
   matching phone. An observed value that does not parse: abstain
   `prerequisite-<name>-unparseable`.
4. Result codes: pass `prerequisite-<name>-confirmed`; fail under `minimum`
   `prerequisite-<name>-below-minimum`; fail under `exact_major` or `equal`
   `prerequisite-<name>-mismatch`. A failed prerequisite returns `unsafe`, as today.
5. `data/recipes-v0.2/avicii.json`: add `"compare": "exact_major"` to `android_version`, and
   set its `source_evidence` to the OpenAndroidInstaller sentence quoted above.
   **Do not add `unlock_class` to avicii.json in this batch.** Its `human_assessment` of
   `unsafe` was carried over from the v0.1 recipe, whose stated reason was that it omitted the
   unlock step. The v0.2 recipe declares it. Whether avicii is still unsafe is a labelling
   decision for the organiser, not a code change. Until it is made, avicii abstains on
   `unlock-class-undeclared`, and A5 makes the build fail if anyone adds the field without
   relabelling. That is the intended protection.
6. `docs/reasoning/recipe-format.md` and `data/schema.md`: document `compare` in one short
   paragraph each, with the two upstream quotes as the reason.

### Tests this section must add

- `required 12, compare exact_major`: observed `"12"` confirmed, `12` confirmed, `"12.1"`
  confirmed, `13` mismatch (unsafe), `11` mismatch (unsafe).
- `required 12, compare minimum`: `13` confirmed, `11` below-minimum (unsafe).
- `required 12`, no `compare`: `cannot-verify`, `comparison-undeclared`.
- observed `"twelve"`: `cannot-verify`, `unparseable`.
- `bootloader_state` `"unlocked"` against `"unlocked"` with no `compare`: confirmed.

## A4. Spacewar: complete the recipe before calling it safe (tracker: v-spacewarsafe)

**Ruling.** Setting `expected_verdict: safe` today would be wrong: the recipe is missing two
things its own source states. `lineage_wiki/_data/devices/spacewar.yml` declares
`before_install: needs_specific_android_fw, version: '15'` and
`before_recovery_install: boot_stack, partitions: [vendor_boot]`. The recipe has neither. With
them added, an unlocked A063 on Android 15 is safe on evidence, and the verdict is earned
rather than declared.

**And no unlocked capture of the Nothing Phone.** Getting one means running
`fastboot flashing unlock` on it, which is on the never-run list, wipes the phone, and is
Tier C. The unlocked case is covered by a test fixture derived from the real record with one
field changed and marked synthetic. It never enters the matrix. An unlocked Spacewar record
enters the matrix only if a tester brings a phone that is already unlocked.

### What to change in `data/recipes-v0.2/spacewar.json`

- Add prerequisite `android_version`: `required "15"`, `compare "exact_major"`,
  `declared_by "before_install.version"`, `source_evidence` quoting the LineageOS sentence.
- Add operation `{"kind": "write-image", "partition": "vendor_boot"}` **before** the existing
  `boot-recovery`, with `declared_by "before_recovery_install.partitions"` if the operation
  format allows a `declared_by`; if it does not, record it in `source_fields_unused` style
  provenance the format already has. Do not invent a new field for it.
- `expected_verdict`: `safe`.
- `expected_verdict_reason`: "An A063 with virtual A/B partitions, an unlocked bootloader and
  Android 15 stock firmware satisfies every precondition the LineageOS install page states."
- Delete `verdict_gap_reason`. There is no gap. If `tests/test_verdict_gap.py` requires the
  field when `expected_verdict` and `human_assessment` agree, fix the test to require it only
  when they differ.

### Tests this section must add (in `tests/test_verify_v2.py`, class `SpacewarRealCaptureTest`)

- Load the real Spacewar record from `data/device-matrix.jsonl` by `product_device`, flatten
  `detected.android` exactly as `data/coverage.py` does. Against spacewar.json: `unsafe`,
  failing on `prerequisite-bootloader_state-mismatch`.
- Same record, `bootloader_state` set to `"unlocked"` in the test only, with a comment saying
  it is synthetic and why no real capture exists: `safe`.
- Same synthetic record, `android_version` `"14"`: `unsafe`, `prerequisite-android_version-mismatch`.
- Same synthetic record, `android_version` removed: `cannot-verify`, `missing-android_version`.

## A5. The gate counts the answer a human gave (tracker: v-opsblind, c-coveragegate)

In `data/coverage.py`:

1. A corpus false safe is **any** run with `verdict == "safe"` where `human_assessment != "safe"`
   **or** `expected_verdict != "safe"`. Build fails on one. Rename nothing else in the file.
2. **Replay every matrix record, not the first per device.** `matrix_fingerprints()` keeps the
   first capture and drops the rest. For testing, every Android record whose `product_device`
   matches a recipe target (case-insensitive, or a `supported_device_codes` alias) is its own
   run. Compute these runs on every invocation. **Do not store `verifier_runs` in any record.**
   Delete the code that reads `verifier_runs` and print the gate from the computed runs.
3. The gate prints two lines from those runs: `false safes == 0` and
   `decided share over paired >= floor`. The floor lives in `data/coverage-floor.json` as
   `{"decided_over_paired": <fraction>, "set": "<date>", "rule": "ratchet: may only go up"}`.
   Set it to the value the replay reports at the end of Part A. Decided share below the floor
   exits 1. A test plants a floor above the current value and asserts exit 1.
4. `tests/test_false_safe_gate.py`: add a run with `expected "cannot-verify"`,
   `human_assessment "unsafe"`, `verdict "safe"` and assert exit 1. That is avicii's shape.

## A6. What the batch 6 reviewer found that is real

Each was reproduced on 17 September. Fix exactly these.

1. `flashguard/verify.py`: append a field to `fields_consumed` **only after** a comparison
   against it has run. `product_model` is currently stamped before the models check, and shows
   up as consumed on a recipe with no model list and a fingerprint with no model.
   Test: that exact case, asserting `product_model` is absent from `fields_consumed`.
2. `tests/test_verify_contract.py::test_model_mismatch_is_unsafe_not_abstention`: use
   `product_device "oriole"` and a model **not** in `SAFE_RECIPE`'s list, and assert the
   reason code is `model-mismatch`. Today it passes on `device-mismatch`.
3. `tests/test_verify_v2.py::test_renamed_unlock_prerequisite_omitted_unlock_class_abstains`:
   delete the `unlock_step` line and the `declared_by` line, so the prerequisite is renamed and
   carries no marker. After A1 that recipe's `write-image` operation makes it abstain on
   `unlock-undeclared-for-operation`. Assert that code. The test now proves the thing it is
   named after.
4. `source.untested` fallback: retire it. A recipe carrying `source.untested` abstains with
   `recipe-untested-legacy-field`. No recipe on disk carries it; confirm with grep and paste.
5. `docs/reasoning/verdict-contract.md`: delete the "Graded variant matching" section and every
   remaining reference to `variant` as a field. Replace with one line pointing to
   `target.models` and the 16 September ruling.
6. `docs/reasoning/recipe-format-coverage.md`: remove the `target.variant` and
   `assets.variant` rows; regenerate the tables from `data/recipe_format_coverage.py` rather
   than editing numbers by hand.
7. `data/recipe_format_coverage.py`: the postmarketOS row matches `^deviceinfo_models=`, a key
   no pmaports device file has. Set that cell to a constant `False` with a comment:
   "pmaports deviceinfo has no model key; the zero is a fact about the format, not a search".
8. `data/recipes-v0.2/a5xelte.json`: the nine-model list cites a source containing no model
   strings. Set `source.device_facts_from` for models to
   `https://wiki.lineageos.org/devices/a5xelte/` and replace the list with the models that page
   declares: `SM-A510F, SM-A510F/DS, SM-A510M, SM-A510Y, SM-A510K, SM-A510L, SM-A510S, SM-A5108`.
   The real capture reports `SM-A510F`, which stays in the list.

## Part A paste-back

```
bash tests/all.sh; echo "ALL RC=$?"
python3 data/coverage.py | sed -n '/CORPUS REPLAY/,$p'
python3 tests/check-recipes.py; echo "RECIPES RC=$?"
grep -rn "is_unlock_step\|unmarked-unlock-step\|bootloader_unlocked\|verifier_runs\|source.untested" flashguard data tests docs --include=*.py --include=*.json --include=*.md | grep -v review-log | grep -v producer-prompt
git --no-optional-locks status --porcelain
```

Expected: `ALL RC=0` or `2`, false safes 0, spacewar `unsafe` on the real capture, the grep
prints only `data/vocabulary.json`'s refused-name entry, the schema table that mirrors it, and
the test that plants it. Commit Part A alone.

---

# PART A7: four corrections found checking Part A (paste this before Part B)

Part A was checked on 17 September by running it and planting defects on a copy. It holds:
both reproduced routes to a false safe now abstain, versions compare as declared, the real
Nothing Phone returns `unsafe`, an unlocked synthetic one returns `safe`, the gate fails the
build on a safe that disagrees with the recipe, and the avicii test fails if anyone classifies
its unlock without relabelling. Four things need correcting. The first is a live route to a
false safe, and the wording that allowed it was in this prompt, not in the code that followed it.

## A7.1 An unlock_class on the wrong prerequisite satisfies the unlock check

### Reproduce first

```
python3 - <<'PY'
import json, copy, sys; sys.path.insert(0, '.')
from flashguard.verify import verify
r = json.load(open('data/recipes-v0.2/spacewar.json'))
r['prerequisites'].pop('bootloader_state')
r['prerequisites']['android_version']['unlock_class'] = 'command'
fp = {"product_device": "Spacewar", "product_model": "A063", "partition_scheme": "virtual_A/B",
      "android_version": "15", "bootloader_state": "locked"}
print("unlock_class on android_version, phone LOCKED ->", verify(fp, r)['verdict'])
PY
```

Expected today: `safe`. A locked phone, a recipe that writes vendor_boot, and nothing checks
the bootloader, because any prerequisite carrying `unlock_class` counts as the unlock step.

### What to change

1. `data/vocabulary.json` gains `"unlock_evidence_fields": {"bootloader_state": "unlocked"}`:
   the fingerprint fields that can evidence an unlock, and the value that means unlocked.
   Mirror it in the schema table; the existing agreement test must cover it.
2. `unlock-undeclared-for-operation` is satisfied only by a prerequisite whose **name** is a key
   of `unlock_evidence_fields`, whose `required` equals that key's value, and which carries an
   `unlock_class` from `unlock_classes`.
3. A prerequisite carrying `unlock_class` whose name is not a key of `unlock_evidence_fields`:
   abstain `unlock-class-on-non-unlock-field`, naming the prerequisite.
4. `tests/check-recipes.py` fails the build on the same two conditions for any recipe on disk.

### Tests

- The reproduction above: `cannot-verify`, with both `unlock-class-on-non-unlock-field` and
  `unlock-undeclared-for-operation`.
- `unlock_class` on `sdk` with `required "35"`, phone locked: `cannot-verify`.
- `bootloader_state` with `unlock_class command` but `required "locked"`: `cannot-verify`,
  `unlock-undeclared-for-operation`.
- `tests/check-recipes.py` against a temp copy of spacewar.json edited as in the reproduction:
  exit 1, message names the recipe and the prerequisite.

## A7.2 The vocabulary has a second copy inside verify.py

`flashguard/verify.py` `_load_vocabulary()` returns a hard-coded copy of the vocabulary when
`data/vocabulary.json` is missing. A clone or package without the file would run on the copy
silently, and the two can drift. Remove the fallback. A missing or unparseable file raises
`RuntimeError("data/vocabulary.json is missing or invalid: the verifier refuses to guess its vocabulary")`
at import. Test: load `flashguard/verify.py` via `importlib` with the path patched to a
non-existent file and assert it raises.

## A7.3 a5xelte's provenance now credits LineageOS for OpenAndroidInstaller's facts

A6.8 asked for the **models** to cite LineageOS. `source.device_facts_from` was replaced
wholesale, so `install_method heimdall_flash_recovery` and the recovery `write-image` now claim
a source they did not come from. Restore `device_facts_from` to the OpenAndroidInstaller
a5xelte.yaml URL and add `"target_models_from": "https://wiki.lineageos.org/devices/a5xelte/"`
to `source`. Document `source.target_models_from` in `docs/reasoning/recipe-format.md` in one
line: present only when the model list comes from a different source than the other facts.
If the recipe validator rejects unknown `source` keys, add it to the validator; do not put it
anywhere else.

## A7.4 The replay report says "recipes" and counts runs

`data/coverage.py` `report_corpus_group` prints `recipes  7` for six v0.2 recipe files, because
it now counts runs (one per matrix record). Print both, on separate lines: `recipes` (distinct
`recipe_id`) and `runs`. `decided` and `paired` stay per run and say so in their labels:
`decided runs`, `paired runs`. Any number that may be quoted in the proposal must say what it
counts.

## Part A7 paste-back

```
bash tests/all.sh; echo "ALL RC=$?"
python3 data/coverage.py | sed -n '/CORPUS REPLAY/,$p'
python3 tests/check-recipes.py; echo "RECIPES RC=$?"
git --no-optional-locks status --porcelain
```

Commit Part A7 on its own, after Part A.

## A7.5 The A7 fixes landed without their tests (paste before committing A7)

Checked on 17 September by running the code: every A7 behaviour is correct. But no test in
`tests/` names `unlock-class-on-non-unlock-field` or the vocabulary `RuntimeError`, so reverting
either fix would leave the suite green. A fix with no test that fails without it is the
pattern this project has paid for most. Tests only; change no product code.

In `tests/test_verify_v2.py`, a new class `UnlockEvidenceFieldTest`, each test building from
`data/recipes-v0.2/spacewar.json` loaded from disk, fingerprint
`{"product_device": "Spacewar", "product_model": "A063", "partition_scheme": "virtual_A/B", "android_version": "15", "sdk": "35"}`
plus the `bootloader_state` given:

1. Remove `bootloader_state` prerequisite, add `unlock_class: command` to `android_version`,
   phone `locked`: `cannot-verify`; codes include `unlock-class-on-non-unlock-field` and
   `unlock-undeclared-for-operation`.
2. Remove `bootloader_state` prerequisite, add prerequisite `sdk`
   `{"state": "OPEN", "required": "35", "compare": "equal", "unlock_class": "command", "declared_by": "test"}`,
   phone `locked`: `cannot-verify`, both codes.
3. Keep `bootloader_state` but set its `required` to `"locked"`, phone `locked`:
   verdict is not `safe`, codes include `unlock-undeclared-for-operation`.
4. Keep the valid `bootloader_state` and also add `unlock_class: command` to `android_version`,
   phone `unlocked`: `cannot-verify`, code `unlock-class-on-non-unlock-field`.

In `tests/test_verify_contract.py` (or a new `tests/test_vocabulary_required.py` run from
`tests/run-verify.sh`): run `python3 -c "import flashguard.verify"` in a subprocess from a temp
copy of `flashguard/` whose sibling `data/` has **no** `vocabulary.json`, and again with a
`vocabulary.json` containing `{bad`. Assert non-zero exit and `refuses to guess` in stderr both
times. Use a subprocess, not `importlib.reload`, so the real module cache is untouched.

In `tests/check-recipes.py`: add the second condition A7.1 asked for, which is missing: a
prerequisite in `unlock_evidence_fields` carrying `unlock_class` whose `required` differs from
the declared value fails. And add a `--self-test` flag that runs `check_recipe` against two
in-memory plants (unlock_class on `android_version`; `bootloader_state` required `locked` with
`unlock_class`) and exits 1 unless both raise. Call `--self-test` from `tests/all.sh` right
after the normal run.

Replace the schema agreement check for `unlock_evidence_fields`: `bootloader_state` appears all
over `data/schema.md`, so "the name occurs somewhere" is always true. Assert the table row
itself: a line containing `unlock_evidence_fields`, `` `bootloader_state` `` and `` `unlocked` ``.

### Paste-back

```
bash tests/all.sh; echo "ALL RC=$?"
python3 tests/check-recipes.py --self-test; echo "SELFTEST RC=$?"
grep -c "unlock-class-on-non-unlock-field" tests/test_verify_v2.py
git --no-optional-locks status --porcelain
```

Then commit A7 and A7.5 together.

---

# PART B: the tester package, final

## B1. The finish screen sends the tester somewhere, in the right order

`bench-kit/START-HERE.html`, `scrFinish()`:

1. **Order.** Today the download button comes before the three wrap-up questions, and the
   answers say "It will be in the downloaded file" even when the file was already downloaded.
   New order: the three questions and Save, then Download, then Send.
   If `S.wrapup` changes after a download, show "You changed your answers after downloading.
   Download again so the file has them."
2. **Send.** After Download, a card titled "Send it back" with:
   - the form link `https://forms.gle/YkdmQvvBQMYQDKXVA`, opened in a new tab;
   - "Attach the one file you just downloaded. Its name starts with `flashguard-`. It already
     contains your descriptors and notes, so there is nothing else to attach.";
   - "The form needs a Google account. If you do not have one, email the file to the address in
     the participation note instead."
3. **No verdict on any screen, ever.** The kit captures. It does not tell a tester whether a
   phone is safe to flash, because a tester who reads "safe" may act on it and this programme
   is Tier A. Add a test in `tests/run-console-logic.js` (or the existing console check) that
   fails if the strings `safe to flash`, `unsafe` or `cannot-verify` appear in
   START-HERE.html outside comments. (Do not match `verdict`: the page already uses it as a CSS
   class for classification agreement, which is not a safety verdict.)
4. Add `kit_version` to `getSessionExportObject()`: a constant at the top of the script,
   `KIT_VERSION = "2026-09-17"`, which B3 stamps. Intake reads it.

## B2. A device that did not appear: ask, do not infer (tracker: r-webusbergo)

WebUSB returns the same `NotFoundError` whether the device was missing from the chooser or the
tester closed it. When it happens, ask one question with two buttons: "My device was not in the
list" (`not_listed`) and "I closed the window" (`tester_cancelled`). Record the answer with
source `tester`. Remove any code path that sets either value without the tester choosing.
Extend the existing console-logic test to assert neither value is set without a click.

On a `file:` page where `navigator.usb` is undefined, the existing message should add one
sentence: "Open this file in Chrome, Edge or Brave. If you already are, tell the organiser
what browser and version this is." Do not claim `file:` is the cause.

## B3. Ubuntu route: the baseline cannot swallow the phone (tracker: c-multidev)

`bench-kit/scripts/00-setup.sh`: after writing the baseline, print every line of it numbered,
and ask: "Is the phone or tablet you are about to test in this list? [y/N]". On `y`: delete
the baseline, say "Unplug it, then run bash 00-setup.sh again", exit 1.

`bench-kit/scripts/01-detect.sh`:
- Diff empty: print "Nothing new since setup. If the device was plugged in when you ran
  setup, it is in the baseline: unplug it, run bash 00-setup.sh, plug it back in, run this
  again." Then the existing cable and port advice.
- Diff has more than one line: print them numbered and ask which one is the device. Never pick.

Neither script may call `adb devices` or `fastboot devices`: both print serials.

Test: `tests/run.sh` gains two cases that stub `lsusb` with a fake on `PATH` (a mouse plus a
USB stick) and assert the prompts fire. No real device.

## B4. One command builds the package, with checksums (tracker: r-package)

1. `bench-kit/MANIFEST.txt`: one path per line, relative to `bench-kit/`, of exactly what a
   tester receives: `START-HERE.html`, `STOP-LIST.txt`, `participation-note.md`,
   `protocol.md`, `example-record.json`, `README.md`, and `scripts/*.sh` listed individually.
2. `tools/build-package.sh`:
   - fails if any MANIFEST path is missing, or if any file under `bench-kit/` is absent from
     MANIFEST and not listed in a short `# excluded:` comment block at the bottom of MANIFEST;
   - fails if `bash tests/all.sh` exits 1;
   - stamps `KIT_VERSION` in a **copy** of START-HERE.html to today's date, never the source;
   - writes `SHA256SUMS.txt` for every packaged file, placed in the package root;
   - writes `dist/flashguard-tester-kit-<YYYY-MM-DD>.zip` with a top folder
     `flashguard-tester-kit/`, and prints its own SHA-256.
3. `.gitignore`: add `dist/`.
4. `bench-kit/README.md`: add a "Checking the files" paragraph: how to compare against
   `SHA256SUMS.txt` on Windows (`certutil -hashfile <file> SHA256`), macOS (`shasum -a 256`)
   and Linux (`sha256sum`), and one sentence: "These checksums cover this kit. Flashguard
   holds no checksum for any ROM, and nothing in this kit checks one."
5. `tests/check-package.sh`, run from `tests/all.sh` under `PACKAGE`: builds into a temp
   directory, unzips, asserts the file list equals MANIFEST plus `SHA256SUMS.txt`, and that
   every checksum verifies. Do not let `check-package.sh` call `all.sh` (recursion): give
   `build-package.sh` a `--skip-suite` flag used only by the check.

## B5. Participation note: one return instruction, and large files

`docs/reference/participation-note.md` and `bench-kit/participation-note.md` (byte-identical,
the suite already checks):
- Replace "Send the records file and the `descriptors/` folder" with the single-file
  instruction from B1.
- Add: "If you attach anything over 1 MB, such as a screen recording, a person looks at it
  before anything from it enters the published dataset."
- Add one sentence for testers without a Google account, matching B1.

## Part B paste-back

```
bash tests/all.sh; echo "ALL RC=$?"
bash tools/build-package.sh; echo "BUILD RC=$?"
unzip -l dist/flashguard-tester-kit-*.zip
grep -c "forms.gle" bench-kit/START-HERE.html
git --no-optional-locks status --porcelain
```

Commit Part B alone. Do not commit `dist/`.

---

# PART C: a returned session becomes data in one command

## C1. `tools/intake.py`

```
python3 tools/intake.py <path/to/flashguard-handle-timestamp.json>          # report only
python3 tools/intake.py <path/to/flashguard-handle-timestamp.json> --write  # write contribution
```

It must, in order, and stop with exit 1 and a plain message at the first failure:

1. Parse the session export. Require `handle`, `session_timestamp`, `records` (non-empty),
   `kit_version`. A missing `kit_version` is allowed only with `--legacy-kit`, and says so.
2. Run `scan_pii` from `data/merge.py` (import it, do not copy it) over the whole file text.
   Any hit: stop, print the hit truncated, write nothing.
3. Refuse any record with `consent_ack` not true, or `detected.android.android_derivation`
   equal to `pending`, naming the record.
4. **No email address in any output.** The Google form collects one; the session file should
   not contain one. If anything matching an email pattern appears in the file, stop.
5. Write `data/contributions/<slug(handle)>-<YYYY-MM-DD of session_timestamp>.jsonl`, one
   record per line, each record gaining `kit_version` and `intake_source: "session_export"`.
   If that file exists, stop; never overwrite. A second session the same day is
   `<slug>-<date>-2.jsonl`.
6. Write each entry of `descriptors` to `tests/real-descriptors/` under its `filename`, refusing
   to overwrite, then run `bash tests/check-descriptor-privacy.sh`.
7. Run `python3 data/merge.py --check`. If it reports problems, delete what steps 5 and 6
   wrote in this run and stop.
8. Print, per Android record: `product_device`, `product_model`, which recipes pair with it,
   and the verdict and non-pass reason codes for each, using the same pairing and flattening
   as `data/coverage.py` (import it). This is for the organiser only. It never goes back to the
   tester.

Without `--write`, steps 5 to 7 run against a temp copy of `data/` and nothing in the
repository changes.

After `--write`, the organiser runs `python3 data/merge.py` then `python3 data/coverage.py`,
and commits the contribution file. Say this at the end of the output.

### Tests (`tests/test_intake.py`, run from `tests/all.sh` under `INTAKE`)

Build session exports in a temp directory from the real Spacewar record: a clean one writes
exactly one contribution file; one with a 15-digit number is refused; one with an email address
is refused; one with `consent_ack: false` is refused; a second run on the same file refuses to
overwrite; the report-only run changes nothing under `data/` (compare a hash of the directory
before and after).

## C2. `docs/reference/testing-runbook.md`

One page, for the organiser. Index it in `docs/INDEX.md`. Sections, in this order, each a
short checklist:

- **Before any invitation goes out.** Build the package with `tools/build-package.sh`, note
  its SHA-256. Open START-HERE.html from the unzipped folder by double-click in Chrome on a
  second machine and read `typeof navigator.usb` in the console; if it is `"undefined"`, stop
  and host the page instead of zipping it. Check free space on the Drive behind the form.
  Send one test submission through the form yourself and confirm it lands.
- **The hackerspace evening, 22 September.** Print STOP-LIST.txt. Each tester uses their own
  handle. Nobody runs any command not in the kit. No one is told a verdict. A device that will
  not connect is recorded as not connecting, never retried with other tools.
- **Remote testers.** One email per tester with the zip and the participation note. What to
  do if they reply "nothing was detected" (point them at the 01-detect message and the cable
  advice, never at a different tool).
- **When a file comes back.** Download from Drive. `python3 tools/intake.py <file>`, read the
  report, then `--write`, `python3 data/merge.py`, `python3 data/coverage.py`, commit. Check
  Drive free space again when the fifth file lands.
- **Changes during testing.** Only defects found by testers. Every change: full suite, rebuild
  the package, new `KIT_VERSION`, and note in the contribution which kit version produced it.
- **Withdrawal.** Delete the tester's contribution file and descriptors, rerun merge, commit.
  Delete their form response and Drive files.

## C3. `docs/reference/form-consent-text.md`

Index it. It is for the organiser to paste into the Google form, not a tester file. Use this
text exactly; the organiser edits it on the form, not here:

> **Before you upload**
>
> The files you send contain information about your device only: its type, model, chipset,
> Android version and similar technical properties. The kit is built so that serial numbers,
> IMEI, MAC addresses and account identifiers are never recorded. I check every file for them
> before anything is used.
>
> Device information from your files is published as open data under CC0, so anyone can reuse
> it. It is labelled with the handle you choose below.
>
> **Your handle is a label, not anonymity.** This form requires a Google account, and I can see
> which account submitted each response. I use that only to contact you if a file looks wrong.
> Your email address is never published: not in the dataset, the code repository, any log or
> any commit.
>
> I keep your form response and uploaded files until the grant decision for this project, and
> no later than 31 December 2027. You can ask me to delete everything you sent at any time by
> emailing the address in the participation note; I will delete your files, your form response
> and your records in the dataset.
>
> If you attach anything larger than 1 MB, I look at it myself before anything from it is used.
>
> If you do not have a Google account, do not stop here: email your file to the address in the
> participation note instead.
>
> ☐ I have read the participation note and agree to the above.

## Part C paste-back

```
bash tests/all.sh; echo "ALL RC=$?"
python3 tests/test_intake.py
git --no-optional-locks status --porcelain
```

Commit Part C alone.

---

# Do not do

- Do not build a verdict screen, a hosted page, an upload endpoint, or a Drive integration.
  The form is the return route for this wave.
- Do not capture, or write instructions to capture, an unlocked device. No unlock, ever.
- Do not add recipes. Six is the corpus for the testing programme; recipes are added only when
  a tester brings a device that has none, and that is after this batch.
- Do not touch the proposal, `grant/`, the claims check or the rule-agreement check. They are
  real and they are not testing.
- Do not store verifier results in records or contributions. They are computed.
