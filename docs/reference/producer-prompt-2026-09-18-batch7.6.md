# Batch 7.6: the kit must not refuse its own output, and the evening runs on a laptop

**Objective.** Batch 7 was checked on 18 September by running it. Part A and Part B hold.
Part C does not: `tools/intake.py` refuses every real session file, and the defect is
reproducible against a descriptor already published in this repository. Separately, the
organiser has said he will run the hackerspace evening on **his own MacBook, or Windows if
the device count forces it**, and three things in the shipped kit assume a Linux session.

This batch fixes defects and closes the platform gap. **It adds no feature.** The freeze
from batch 7 stands: after this, only defects testers find get fixed.

Three parts, in order. **Stop at the first part whose paste-back fails** and say which
command failed. Commit after each part on its own.

## Ground rules for every section

- The suite is `bash tests/all.sh`. **pytest is not installed on this machine.** Do not
  write paste-back commands that use it. Unit tests run with `python3 tests/<file>.py`.
- Do not change `data/device-matrix.jsonl` or anything in `data/contributions/` by hand.
  They are captured evidence.
- Do not touch `docs/tracker/` or anything under `library/`.
- Do not widen a gate, a scanner or a refusal to make a test pass. If a test and a gate
  disagree, say which and stop. **In particular: no allowlist entry, in any scanner, for
  any file.** An exemption inside a scanner is the scanner agreeing not to notice.
- Do not add a second name for anything. Every section that removes a name removes it
  everywhere, including comments and docs.
- `verify()` stays a pure function. This batch does not touch `flashguard/`.
- Never run anything on the never-run list in `CLAUDE.md`. Nothing here needs a device.
- Every fix in Part D was reproduced on 18 September. Reproduce it again before fixing it.
  If a reproduction does not reproduce, stop and say so rather than fixing forward.

---

# PART D: intake does not refuse the kit's own output

## D1. The privacy note is read as a privacy leak (defect, blocking)

### Reproduce first

```
python3 - <<'PY'
import json, copy, pathlib, sys, subprocess, tempfile
sys.path.insert(0, 'tests')
from test_intake import get_real_spacewar_record
real = sorted(pathlib.Path("tests/real-descriptors").glob("*.desc"))[0]
content = real.read_text()
print("descriptor:", real.name, "| contains the word iSerial:", "iSerial" in content)
rec = copy.deepcopy(get_real_spacewar_record()); rec["record_id"]="probe"; rec["consent_ack"]=True
sess = {"kit_version":"2026-09-17","handle":"probe","host_platform":"ubuntu_installed",
 "host_shell":"not_applicable","session_timestamp":"2026-09-17T12:00:00Z","session_notes":"",
 "manifest":{"devices_read":1,"descriptors_count":1,"android_fingerprints":1},
 "records":[rec],
 "descriptors":[{"filename":"probe.desc","content":content,"device":"x","route":"browser",
   "expect":"adb","ground_truth":"tester_identified","captured":"2026-09-17T12:00:00Z"}]}
d = pathlib.Path(tempfile.mkdtemp()); f = d/"flashguard-probe.json"
f.write_text(json.dumps(sess, indent=2))
r = subprocess.run([sys.executable,"tools/intake.py",str(f)],capture_output=True,text=True)
print("intake exit:", r.returncode); print(r.stderr.strip()[:200])
PY
```

Expected today: exit 1, `forbidden field name: iSerial`. If not, stop and say so.

### What is actually wrong

`01-detect.sh` writes this header line into every descriptor it saves:

    #!note=Captured on a real device. iSerial dropped and embedded SN masked. EDIT #!expect to the

`merge.FORBIDDEN` is `\b(imei|imsi|iccid|serialno|serial_no|iSerial|android_id)\b`, unanchored.
`intake.py` runs it over the **whole session file text**, descriptor contents included. So the
sentence that proves the serial was stripped is read as the serial.

`tests/check-descriptor-privacy.sh` gets this right and has all along: it anchors,
`^[[:space:]]*iSerial`, which is the line `lsusb -v` actually prints. The kit's note is not
that line.

**Do not change the note.** It is correct and it is the thing a reviewer reads first.
**Do not delete `iSerial` from `FORBIDDEN`.** A record field genuinely named `iSerial` must
still fail.

### What to change

1. In `data/merge.py`, split the one pattern into two, and say why in a comment naming this
   defect and its date:
   - `FORBIDDEN` keeps `imei|imsi|iccid|serialno|serial_no|android_id` as a word match. These
     are field names; a record that contains the word has a problem.
   - `iSerial` moves to its own anchored pattern matching the `lsusb -v` line only, the same
     shape `check-descriptor-privacy.sh` uses: start of line, optional whitespace, `iSerial`,
     whitespace, then a value. `scan_pii` reports it with the same label it reports today.
2. `scan_pii` gains no new signature and no new caller. Both patterns run in the same loop.
3. `scan_pii` also does **not** catch the embedded `_SN:` form, which is the leak this
   project actually found in the wild on 13 September. Add it, with the same allowance
   `check-public-safe.sh` already declares for masked values (`<stripped>`, `<the serial>`).
   A masked serial is the evidence that stripping worked; an unmasked one is the leak.

### Tests this section must add

In `tests/test_intake.py`:

- **The fixture must resemble the artefact.** The clean-export test currently builds a
  descriptor string by hand, with no `#!note` line, so it tests a descriptor the kit cannot
  produce. Replace its `content` with a real file read from `tests/real-descriptors/`, chosen
  by `sorted(...)[0]` so it does not name one file. Assert intake exits 0.
- A descriptor whose content carries a genuine `lsusb -v` serial line
  (`  iSerial                 3 <some value>`): intake exits 1 and stderr names it.
- A descriptor whose content carries `_SN:` with an unmasked value: intake exits 1.
- A descriptor whose content carries `_SN:<stripped>`: intake exits 0.

In `tests/test_contributions_validation.py` or alongside it: `scan_pii` on the kit's exact
note line returns no problem, and on the real `lsusb` line returns one. **Assemble any
digits in these fixtures at runtime from short pieces**, as `tests/test_intake.py` already
does for `IMEI_SHAPED`, so no tracked file carries a 15-digit literal.

## D2. A descriptor filename is untrusted input (defect)

### Reproduce first

```
python3 - <<'PY'
import json, copy, pathlib, sys, subprocess, tempfile
sys.path.insert(0,'tests')
from test_intake import get_real_spacewar_record
rec = copy.deepcopy(get_real_spacewar_record()); rec["record_id"]="probe2"; rec["consent_ack"]=True
sess = {"kit_version":"2026-09-17","handle":"probe2","host_platform":"ubuntu_installed",
 "host_shell":"not_applicable","session_timestamp":"2026-09-17T12:00:00Z","session_notes":"",
 "manifest":{"devices_read":1,"descriptors_count":1,"android_fingerprints":1},
 "records":[rec],
 "descriptors":[{"filename":"../../ESCAPED.txt","content":"should never be written here\n",
  "device":"x","route":"browser","expect":"adb","ground_truth":"unidentified",
  "captured":"2026-09-17T12:00:00Z"}]}
d = pathlib.Path(tempfile.mkdtemp()); (d/"repo"/"tests").mkdir(parents=True)
f = d/"s.json"; f.write_text(json.dumps(sess, indent=2))
r = subprocess.run([sys.executable,"tools/intake.py",str(f),"--write",
  "--contrib-dir",str(d/"contrib"),"--descriptors-dir",str(d/"repo"/"tests"/"real-descriptors")],
  capture_output=True,text=True)
print("exit:", r.returncode)
print("escaped:", (d/"repo"/"ESCAPED.txt").exists())
PY
```

Expected today: `exit: 0`, `escaped: True`. If not, stop and say so.

### What to change

`intake.py` writes `dest_descriptors_dir / desc["filename"]` with no check. That filename
comes from `_descriptor_file` in a `BENCH_CAPTURE` line the tester pastes into the page, so
it is untrusted input under the same rule that already covers recipes in `CLAUDE.md`.

A descriptor filename must be a **bare name**: no `/`, no `\`, not absolute, not `.` or `..`,
and it must end in `.desc`. Anything else exits 1 naming the filename, before anything is
written. Do not sanitise and continue; do not rename it to something safe. A file the tool
cannot name is a file the organiser should look at.

### Tests this section must add

The reproduction above, asserting exit 1 and that nothing was created; the same for an
absolute path; the same for a name not ending in `.desc`; and one bare valid name that still
succeeds, so the check cannot be satisfied by refusing everything.

## D3. The dry run checks what it says it checks (defect)

Report-only writes descriptors into a temp directory and never calls
`check-descriptor-privacy.sh`. `--write` calls it only when the destination is the real
`tests/real-descriptors/`, which no test uses. So the descriptor privacy step is exercised by
nothing, and the run the runbook tells the organiser to read first prints
`validated successfully` without having looked. The form consent text says *"I check every
file for them before anything is used"*, and today the tool does not.

### What to change

1. `tests/check-descriptor-privacy.sh` takes an **optional directory argument**. With none,
   it scans the directories it scans today and its output is unchanged. With one, it scans
   that directory instead. Do not add a second script and do not duplicate the patterns.
2. `intake.py` runs it against whichever descriptors directory this run is writing to, real
   or temporary, in **both** report-only and `--write`. In report-only a failure exits 1 with
   the script's own output; in `--write` it triggers the rollback that already exists.
3. The report-only success line must say what it checked, by name, rather than
   `validated successfully`.

### Tests this section must add

- A session whose descriptor content carries a real `lsusb` serial line: **report-only**
  exits 1. This is the test that fails without the fix.
- `tests/check-descriptor-privacy.sh` with a directory argument on a clean temp directory:
  exit 0; on one with a planted serial: exit 1.
- `tests/check-descriptor-privacy.sh` with no argument prints the same line it prints today.

## D4. Pairing is imported, not copied

`intake.py` reimplements `data/coverage.py`'s `corpus_runs` matching inline: recipe loading,
codename lowercasing, `supported_device_codes` aliases, the `dict(android)` flattening. Batch
7 Part C said to import it. Two copies of the pairing rule can drift, and then the organiser's
intake report and the build gate disagree about the same device on the same evening. This is
the shape of A7.2, which was the vocabulary's second copy inside `verify.py`.

Import `data/coverage.py` and use its pairing and flattening. If a function has to be
extracted from `coverage.py` to make it importable, extract it there and call it from both;
do not copy it back. `coverage.py`'s own output must not change: assert that by running it
before and after and diffing.

### Test this section must add

One test asserting `intake.py` and `data/coverage.py` produce the same verdict and the same
non-pass reason codes for the real Spacewar record against `spacewar.json`, by calling both.
Not by comparing two hard-coded strings.

## D5. One more directory the privacy check does not look at

`01-detect.sh` writes live captures to `bench-kit/descriptors/`. That directory is not in
`.gitignore` and not in `check-descriptor-privacy.sh`'s `DIRS`. It is the same directory blind
spot the script's own comment was written about, one directory over.

Add `bench-kit/descriptors/` to `.gitignore` **and** to the script's `DIRS` list. Both: the
gitignore stops it reaching GitHub, the `DIRS` entry means the organiser finds out before he
copies something out of it by hand. Confirm `tests/check-package.sh` still passes, since
MANIFEST already excludes `descriptors`.

## Part D paste-back

```
bash tests/all.sh; echo "ALL RC=$?"
python3 tests/test_intake.py
bash tests/check-descriptor-privacy.sh; echo "PRIVACY RC=$?"
python3 data/coverage.py | sed -n '/CORPUS REPLAY/,$p'
git --no-optional-locks status --porcelain
```

Expected: `ALL RC=0` or `2`, corpus replay unchanged from before this batch, false safes 0.
Commit Part D alone.

---

# PART E: the evening runs on the organiser's own laptop

**The situation.** The hackerspace evening is 22 September. The organiser will run it on his
own MacBook, or on Windows if the number of devices forces a second machine. Neither is a
Linux session, and three things in the shipped kit assume one. Nothing below changes what the
verifier does; it changes what the kit truthfully claims and closes one hole that Part B of
batch 7 opened.

**The three consequences, established by reading the kit on 18 September.** State them in the
runbook in these words, because each one will otherwise look like a defect on the night:

1. **`00-setup.sh` and `01-detect.sh` are Linux-only.** They call `lsusb`, and `00-setup.sh`
   installs via `apt`. On macOS and Windows the only descriptor route is the browser.
2. **Chromium refuses whole device classes** — mass storage, HID, audio, video — so on a
   laptop evening most USB sticks, cameras and e-readers **cannot be captured by any route**.
   Those are the negatives, and the Tier A exit criterion counts them. A drawer evening on a
   Mac produces mostly Android positives. That is a property of the platform, recorded as a
   finding, never retried with another tool.
3. **Windows produces `android_derivation: "pending"` on every Android record**, and
   `merge.py` and `intake.py` both refuse pending. See E2.

## E1. `protocol.md` still tells the tester to boot Ubuntu

`bench-kit/protocol.md` step 1 is *"Boot from the Ubuntu stick, choose Try Ubuntu"*, and
"What you need" asks for a computer that can boot from a USB stick. `START-HERE.html` has
offered five platforms since 14 September. The tester-facing file and the tool disagree, and
the file is what a tester reads first.

Rewrite "What you need" and "What you do" so that the page chooses the route and the file does
not. Keep it short. The Ubuntu stick becomes one of the options the page offers, named as the
one that reads the most devices and takes the longest, not as the first step. Steps 3, 4 and 5
must say they belong to the Linux routes. Do not add a platform table; the page has one.

`bench-kit/README.md` already says the stick should be ExFAT or FAT so macOS and Linux can both
read it. Leave that.

**No placeholders.** `tests/check-index.sh` exits 2 on them and that blocks recruitment.

## E2. A Windows session must not be a dead end

`data/schema.md` already says pending records "are refused by `merge.py` until derivation has
been executed via `derive.sh` on the maintainer's machine". **That step has no tool.** The
schema documents a workflow nobody can run, and batch 7 shipped the Windows capture path that
produces its input.

This is wiring an existing pure function, not new logic. Keep it that size.

1. **`tools/derive-pending.py`.** Reads a session export. For every record carrying
   `detected.android.android_raw` and `android_derivation: "pending"`, pipes the raw property
   text through `bench-kit/scripts/derive.sh` (subprocess, stdin to stdout, as
   `tests/run-android.sh` already does) and writes the derived fields into the record, setting
   `android_derivation: "derived"`. `derived` is already the declared second value in
   `data/schema.md`; do not invent a third.
   - It writes a **new** file next to the input, `<name>-derived.json`, and refuses to
     overwrite. The tester's file is evidence and is never edited in place.
   - It changes nothing else in the record: not `android_raw`, not `capture_route`, not
     `host_platform`, not `host_shell`. A record with no `android_raw` passes through byte
     for byte.
   - It requires bash. It will not run on Windows. Say so in its `--help` and in the runbook:
     a Windows evening's files are derived afterwards, on the Mac.
   - **Do not call it from `intake.py`.** Derivation is a step the organiser takes knowingly,
     and chaining it would mean intake silently rewriting a tester's data.
2. **`intake.py`'s pending refusal must say what to do.** Today it names the record and stops.
   It must also name `tools/derive-pending.py`, and say that the file is recoverable rather
   than rejected. It still refuses the whole file, which is correct: a half-derived session is
   worse than a refused one.

### Tests this section must add (`tests/test_derive_pending.py`, run from `tests/all.sh`)

`tests/android/*.props` are real raw property sets and are exactly this tool's input. Build
session exports from them in a temp directory. No device.

- `samsung-a5-2017-android8.props` as a pending record: after derivation
  `android_derivation` is `derived`, and `partition_scheme`, `bootloader_state` and
  `chipset_family` match what `bash bench-kit/scripts/derive.sh` returns for the same input.
  Compare against the script's output, not against values written into the test.
- `empty-everything.props`: derivation succeeds and the fields it cannot establish are
  `unknown`. Deriving nothing is a valid answer and must not be an error.
- A record with no `android_raw` is unchanged, compared by JSON equality.
- Running twice refuses the second time.
- A derived file then passes `python3 tools/intake.py` where the pending original did not.
  That is the test that proves the dead end is closed.

## E3. The runbook says what to do on the night

`docs/reference/testing-runbook.md`. Edit in place; keep the checklist shape.

1. **"Before any invitation goes out"** — the WebUSB check currently says "a second machine".
   Change it to the exact laptop, browser and browser version being used on the evening,
   opened from the unzipped folder by double-click, reading `typeof navigator.usb` in the
   console. A pass on a different machine proves nothing about this one.
2. **New pre-flight items for a laptop evening:** `adb` installed and on `PATH`
   (`brew install android-platform-tools` on macOS); `bash bench-kit/scripts/derive.sh`
   runs from the evening's laptop; `python3 tools/intake.py` runs from it; and one full
   rehearsal — capture one device, download the file, run intake report-only — **on the
   evening's laptop, before anyone is invited**. That rehearsal is what would have caught D1.
3. **A platform section**, carrying the three consequences listed at the top of Part E in
   plain words, including that uncapturable sticks and cameras are recorded as such.
4. **"When a file comes back" gains a refusal branch.** What each intake refusal means and
   what to do: PII hit (look at the file, do not edit it, ask the tester); consent not
   acknowledged (do not write it, ask); pending derivation (run `tools/derive-pending.py`);
   descriptor filename refused (look at it by hand); file already exists (`--session-number`).
   And the rule under pressure: **never `--no-verify`, never edit a tester's file to make a
   check pass.** A refused file waits. It does not get fixed at 21:40 with five people in the
   room.
5. **Say where intake runs.** Files may be handed over at the hackerspace, but intake,
   derivation, merge and commit happen afterwards, on the laptop, not between testers.
6. **Withdrawal is incomplete.** It names `data/contributions/` and `tests/real-descriptors/`.
   Add `tests/webusb-fixtures/` and `bench-kit/descriptors/`, and a line saying withdrawal
   means every directory a descriptor can reach. A withdrawal promise that misses a directory
   is worse than no promise.

## Part E paste-back

```
bash tests/all.sh; echo "ALL RC=$?"
python3 tests/test_derive_pending.py
bash tools/build-package.sh; echo "BUILD RC=$?"
unzip -l dist/flashguard-tester-kit-*.zip
grep -n "Try Ubuntu" bench-kit/protocol.md; echo "UBUNTU-ONLY LINES: $?"
git --no-optional-locks status --porcelain
```

Expected: `ALL RC=0` or `2`, the grep finds nothing, the package still builds. Do not commit
`dist/`. Commit Part E alone.

---

# PART F: three small true things

1. **`docs/INDEX.md` lists `docs/Research/variant-danger-findings.md` twice**, with two
   different descriptions. Keep the fuller one, delete the other. Then make
   `tests/check-index.sh` fail on a duplicate path in INDEX.md, since it did not notice.
2. **Index the two new files** if they are not already indexed:
   `docs/reference/producer-prompt-2026-09-18-batch7.6.md`, and anything Part E created.
   `check-index.sh` fails the build on an unindexed document, which is how batch 7 Part C was
   blocked.
3. **Write down that there are three PII scanners with three different patterns**, in a
   comment at the top of `data/merge.py` and nowhere else: `LEAKS` in `START-HERE.html` runs
   at paste time in the browser, `scan_pii` runs over records and session files,
   `check-descriptor-privacy.sh` and `check-public-safe.sh` run over files at rest. They
   deliberately differ, because they see different text at different moments. D1 happened
   because nobody had written that down. **Do not unify them in this batch.** Naming the
   arrangement is the deliverable.

## Part F paste-back

```
bash tests/all.sh; echo "ALL RC=$?"
bash tests/check-index.sh; echo "INDEX RC=$?"
grep -c "variant-danger-findings" docs/INDEX.md
git --no-optional-locks status --porcelain
```

Commit Part F alone.

---

# Do not do

- Do not add an allowlist entry to any scanner, for any file, including a test file.
- Do not change the `#!note` line in `01-detect.sh`, or remove `iSerial` from the forbidden
  names. Both are correct; the matching was wrong.
- Do not write a macOS or Windows equivalent of `01-detect.sh`. `system_profiler` and
  PowerShell USB enumeration are a new capture route, they would need their own fixtures and
  their own agreement tests, and there are four days. The browser is the route on a laptop.
- Do not make `intake.py` derive, repair, rename or edit anything in a tester's file.
- Do not touch `flashguard/`, `data/vocabulary.json`, `data/recipes-v0.2/` or the coverage
  floor. Nothing in this batch is a verifier change.
- Do not act on the two research files in `docs/Research/`. They contain two different
  proposed vocabularies for browser visibility, and the schema already has
  `browser_enumeration`. Naming that is a decision after testing, not a batch.
- Do not add recipes, and do not capture an unlocked device.
