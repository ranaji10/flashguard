# Build task: one tester file, two steps, three platforms

**Deadline: Tuesday 15 September.** This is used in a room with strangers holding
phones, not demoed. Scope is protected below. Read the whole task before writing code.

## What exists. Build on it, do not restart.

- `bench-kit/START-HERE.html` (1002 lines) is already the tester's guided flow: a screen
  state machine (`scrBoot` → `scrPrep` → `scrBootUp` → `scrWho` → `scrSetup` → `scrLoop` →
  `scrIdentify` → `scrPhonePrep` → `scrRun` → `scrFinish`), a record store `S` persisted to
  `localStorage`, `parseCapture()` which ingests a `BENCH_CAPTURE {...}` line pasted from a
  terminal, `leakIn()` which refuses text containing serial/IMEI/MAC shapes, `DEVICES`,
  `CLASSES`, `USB_MODES`, `slug()`, and a `device-matrix.jsonl` download. **Reuse all of it.**
- `tests/webusb-probe.html` reads devices over WebUSB, masks embedded serials, records
  `browser_enumeration` for a device that did not appear, and exports a whole session as one
  file. Proven on macOS/Brave, Windows/Edge and Ubuntu/Chrome 152, including from a zip that
  was emailed, unzipped and opened by double-click.
- `bench-kit/scripts/02-android.sh` reads seventeen allowlisted `adb shell getprop` values
  and prints one `BENCH_CAPTURE` line. It needs **only `adb` on PATH**. It does not need
  `lsusb`, the baseline, or `01-detect.sh`.
- `bench-kit/scripts/01-detect.sh` needs `lsusb` and a baseline diff, so it is Linux-only.
- `tests/test-webusb-agreement.sh` asserts `classify.sh` returns the same class from a
  browser-captured `.desc` and an `lsusb` one. It reads `tests/webusb-fixtures/*.desc`, not
  the probe HTML.

## The decisions are already made. Do not re-open them.

**1. Step 1 is identical on every platform. Only step 2 varies.**
The browser replaces `01-detect.sh` completely: WebUSB yields manufacturer, product, both
IDs, device class, USB version and every interface class/subclass/protocol, which is the
entire input to `classify.sh`. Do not branch step 1 by platform. Do not ask for a platform
before step 1.

**2. What the platform actually changes is three sentences, not a protocol.**
How to get `adb`, how to open a terminal, and the exact command to run. The fields captured,
the allowlist and the record shape are identical on all three. If you find yourself writing
platform-specific *capture logic*, stop: you have gone wrong.

**3. Ask the platform. Never detect it.**
A `userAgent` guess that is wrong sends a tester down instructions for a machine they are not
using, and they will follow them anyway. Record it as `host_platform` with the values
`macos | windows | ubuntu_live | ubuntu_installed | linux_other | not_stated`. Absence means
`not_stated`, never an assumption.

**4. Windows has no bash, and that decides step 2's mechanism.**
Two paths, both ending in the same stored data:
- **Where bash exists** (Ubuntu, macOS, Git Bash, WSL): `bash 02-android.sh`, unchanged. It
  prints a `BENCH_CAPTURE` line the page already parses. This path stores DERIVED fields.
- **Everywhere else** (plain Windows PowerShell or cmd): the page shows one pasteable block
  of `adb shell getprop <key>` commands over the same seventeen keys, and the tester pastes
  the RAW output back. The page stores that text **verbatim** under `android_raw`, sets
  `android_derivation: "pending"`, and derives nothing.

**DO NOT reimplement `derive.sh` or `classify.sh` in JavaScript.** Deriving in two languages
is how two implementations of one rule quietly disagree, and this repository has been bitten
by that class of defect nine times. The raw text is derived later, on the maintainer's
machine, by the existing `derive.sh`.

**5. The pasted-text leak check applies to the raw path too, and is not optional.**
A tester pasting terminal output can paste anything, including `adb devices`, which prints
the device serial. Run the existing `leakIn()` over any pasted text before it is stored and
refuse with the existing message. This is the exact defect that put a real serial in this
repository for fourteen days.

**6. One file goes to the tester, one file comes back.**
`bench-kit/START-HERE.html` is the only file a tester opens. Move the WebUSB reading code
into it. Leave `tests/webusb-probe.html` on disk but add a header comment saying it is
superseded and kept only as the provenance of `tests/webusb-fixtures/`; the live reader is in
START-HERE.html. There must be exactly ONE live copy of the reading code.

The export is a single file named `flashguard-<handle>-<UTC timestamp>.json`, containing:
`handle`, `host_platform`, `records[]`, `descriptors[]` (each carrying the same five `#!`
header fields the fixtures use: `expect`, `ground_truth`, `device`, `route`, `captured`, plus
the raw descriptor text), session notes, and a `manifest` with counts. **The handle goes
INSIDE the file as well as in its name**, because a filename is a convenience and people
rename things. Keep the existing per-`.desc` download as a second, separate button for the
maintainer's use.

**7. `capture_route` is per capture, not per session.** Step 1 writes `browser`. Step 2
writes `adb_host` when run from the tester's own OS, or `linux_live` from the Ubuntu stick.
Add `adb_host` to `data/schema.md` with the same "absence is not a value" wording the other
fields use.

**8. The Ubuntu stick stays**, as one of the platform choices, not as the default. Its
existing screens (`scrPrep`, `scrBootUp`) become the `ubuntu_live` branch of step 2. Do not
delete them. The 90-minute figure belongs only to that branch, and most of it is stick-making
— say so where it is shown.

## Explicitly out of scope for Tuesday

Do not build: any upload to Drive or the form beyond opening the form URL in a new tab; zip
building in the browser; platform auto-detection; ADB-over-WebUSB; any change to
`classify.sh`, `derive.sh`, `verify.py` or the recipe format; any new dependency of any kind.
The page must remain a single self-contained HTML file with no external requests.

## What must still be true when you are done

Run `bash tests/all.sh`. It must end at its usual soft exit 2, with nothing newly failing.
Then, specifically:

1. `tests/check-portability.sh` still passes. Anything you touch in `bench-kit/scripts/` must
   run under bash 3.2, which is what macOS ships. No `declare -A`, no `${x^^}`, no
   `mapfile`. This has broken three times.
2. `tests/check-descriptor-privacy.sh` still reports every fixture clean.
3. `tests/test-webusb-agreement.sh` still passes, and the descriptors START-HERE.html now
   exports still satisfy it. Prove this by exporting one and running the test against it.
4. **A new test, and it is the one that matters.** Assert that the bash path and the
   raw-paste path, given the same seventeen key/value pairs from the same phone, produce the
   same derived fields once `derive.sh` has run over the raw one. Two routes to one answer is
   the pattern `test-webusb-agreement.sh` already establishes; follow it. A test that has
   never failed is a comment, so plant a discrepancy, watch it fail, then restore.
5. Open the exported JSON and confirm the handle is inside it, not only in the filename.
6. Zip `bench-kit/`, unzip it somewhere new, open START-HERE.html by double-click, and
   complete step 1 with a real phone. If that does not work, nothing else matters.

## How to hand this back

Work in small commits, each one whole. Do not leave the tree mid-repair: a turn that ends
because the meter ran out is the same problem as a turn too large to review.

When finished: `bash tests/handoff.sh`, then `bash tests/review-packet.sh` and give its
output — and nothing else, no summary — to a fresh reviewing session in a different model
family.

## Where you will be tempted to go wrong

- Guessing the platform to save the tester a click. Ask.
- Deriving the Android fields in JavaScript because it is only twenty lines. It is two
  implementations of one rule.
- Treating a missing `host_platform`, a missing `browser_enumeration` or a missing
  `partition_scheme` as a value. A browser-only Android record must write
  `partition_scheme: "unknown"`, never `not_applicable`: the schema says `not_applicable`
  means the field cannot apply, and it applies to every Android phone.
- Improving the parts of the bench kit that are not blocking a tester. They are frozen.
