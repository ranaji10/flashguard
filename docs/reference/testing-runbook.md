# Testing Runbook

*Organiser runbook for tester invitations, the hackerspace evening on 22 September, the remote wave, file intake, and withdrawal.*

---

## Before any invitation goes out

- [ ] **Build package:** Run `bash tools/build-package.sh` and record the generated ZIP archive SHA-256 checksum.
- [ ] **Verify WebUSB offline on the target laptop:** Open `START-HERE.html` from the unzipped package folder by double-clicking in Chrome (or Chromium browser) on the exact laptop, browser and browser version being used on the evening. Open the developer console and check `typeof navigator.usb`. If it evaluates to `"undefined"`, stop and host the page over HTTPS instead of distributing as a zip file. A pass on a different machine proves nothing about this one.
- [ ] **Check adb on PATH:** Ensure `adb` is installed and reachable on `PATH` (`brew install android-platform-tools` on macOS).
- [ ] **Verify derive.sh execution:** Verify `bash bench-kit/scripts/derive.sh` runs from the evening's laptop.
- [ ] **Verify intake.py execution:** Verify `python3 tools/intake.py` runs from the evening's laptop.
- [ ] **Full pre-flight rehearsal:** Conduct one full rehearsal on the evening's laptop before anyone is invited — capture one device, download the session file, and run intake report-only (`python3 tools/intake.py <file>`).
- [ ] **Check Drive storage:** Verify available free space on the Google Drive account configured behind the intake form.
- [ ] **Dry-run submission:** Send one test submission through the Google form and confirm that the upload lands in Drive and the response is logged.

## Platform constraints on a laptop evening

The hackerspace evening runs on the organiser's own laptop (macOS, or Windows if device count forces a second machine). Three platform properties apply:

1. **`00-setup.sh` and `01-detect.sh` are Linux-only.** They call `lsusb`, and `00-setup.sh` installs via `apt`. On macOS and Windows the only descriptor route is the browser.
2. **Chromium refuses whole device classes** — mass storage, HID, audio, video — so on a laptop evening most USB sticks, cameras and e-readers **cannot be captured by any route**. Those are the negatives, and the Tier A exit criterion counts them. A drawer evening on a Mac produces mostly Android positives. That is a property of the platform, recorded as a finding, never retried with another tool.
3. **Windows produces `android_derivation: "pending"` on every Android record**, and `merge.py` and `intake.py` both refuse pending. Files from Windows sessions are derived afterwards on macOS/Linux using `tools/derive-pending.py`.

## The hackerspace evening, 22 September

- [ ] **Print STOP-LIST:** Print copies of `bench-kit/STOP-LIST.txt` and keep them visible at testing stations.
- [ ] **Unique handles:** Ensure each participant chooses and uses their own distinct handle.
- [ ] **Kit commands only:** Enforce that nobody runs any command or tool outside the provided kit.
- [ ] **No verdicts:** Never disclose or communicate a safety verdict to any tester (Tier A data collection only).
- [ ] **Record failures honestly:** If a device will not connect, record it as not connecting; never retry with unauthorized tools or commands.
- [ ] **Intake location:** Files may be handed over at the hackerspace, but intake, derivation, merge and commit happen afterwards, on the laptop, not between testers in the room.

## Remote testers

- [ ] **Send kit:** Send one email per tester containing the ZIP package and `participation-note.md`.
- [ ] **Support policy:** If a tester replies that "nothing was detected", direct them to the `01-detect.sh` terminal output, port, and cable troubleshooting advice; never suggest alternative tools or unauthorized scripts.

## When a file comes back

The whole path from "a tester submitted the form" to "their records are in the dataset". Do it at a desk, never in the room. Every command runs from `project/`.

**1. Collect.** Download the tester's upload from the Google Drive folder behind the form. Save it to
`raw/<YYYY-MM-DD>/<handle>/`. `raw/` is gitignored, so nothing there can be committed by accident.

**2. Keep one file per session.** Only `flashguard-<handle>-<timestamp>.json` matters. It already holds the descriptors and the device matrix, so ignore any `.desc` or `device-matrix.jsonl` the tester attached as well.
If they sent two `flashguard-` files from the same session (they pressed Download twice), check that the files differ only in `session_timestamp`, then use the newer one:

    diff <(python3 -m json.tool OLDER.json) <(python3 -m json.tool NEWER.json)

If more than that line differs, these are two sessions. Take both in, the second with `--session-number 2`.

**3. Windows sessions only: derive first.** If the file says `"host_platform": "windows"`, its Android records are `pending`. On the Mac:

    python3 tools/derive-pending.py raw/<date>/<handle>/flashguard-....json

That writes a new file beside the original with `-derived` added before `.json`: `flashguard-sam-2026-09-22T08-25-52-959Z.json` becomes `flashguard-sam-2026-09-22T08-25-52-959Z-derived.json`. Use the derived file from here on. Never edit the original.

**4. Dry run.**

    python3 tools/intake.py raw/<date>/<handle>/flashguard-....json

This writes nothing. It ends in one of two ways:

- **It prints a PAIRING & VERIFICATION REPORT.** The file is clean. Go to step 5.
- **It prints a refusal.** Look it up here. Do not edit the file to make it pass.

| Refusal says | What it means | What to do |
|---|---|---|
| `embedded serial: _SN:...` | A device put its serial inside its product name (Nothing Phone 1: `YUPIK-QRD _SN:...`). Kits before 2026-09-19 copied it in through the browser. That was the kit's fault, not the tester's. | Do not take it in. Ask the tester to capture that phone again with the current kit and send the new file. |
| other PII, forbidden field, serial | Something identifying is in the file | Look at it, do not edit it, ask the tester |
| `consent_ack` not true | Consent box was never ticked | Do not take it in; ask the tester |
| `android_derivation: pending` | Windows file, step 3 skipped | Do step 3 |
| descriptor filename refused | A descriptor name is not a bare `*.desc` | Look at it by hand |
| contribution file already exists | Second session from the same handle on the same day | Add `--session-number 2` |
| missing `kit_version` | A kit from before version stamping | `--legacy-kit`, only if you know which kit it was |

A refused file waits. Never use `--no-verify`, and never fix a tester's file by hand.

**5. Read the report, keep it to yourself.** For each Android record it names the recipes it paired with and the verdict. This is for you. **Never pass a verdict on to a tester.** If any record comes back `safe`, check it before anything else: a false safe is the one error this project cannot make.

**6. Write, merge, check, commit.**

    python3 tools/intake.py <file> --write
    python3 data/merge.py
    python3 data/coverage.py
    bash tests/all.sh

Commit the new `data/contributions/<handle>-<date>.jsonl` and its descriptors. Note in the commit message which kit version produced the file.

**7. Close the loop.** Reply to the tester with a thank-you and, if they wrote any notes, what you are doing about them. Check Drive's free space when the fifth file arrives.

### First round, 18 September: what happened

Three author sessions (macOS, Windows, Ubuntu), each downloaded twice. All three were refused at step 4 for the embedded serial above: the browser route never masked it, though `01-detect.sh` did. With the serial masked in a scratch copy (diagnosis only, not taken in), all three passed every other check. They also gave the same verdicts on all three platforms: Nothing Phone 1 `unsafe` (bootloader locked), Samsung A5 `cannot-verify` (partition scheme unknown). No false safes. The kit now masks at capture (`maskSerial` in START-HERE.html, tested in `run-console-logic.js`).

## Changes during testing

- [ ] **Defect fixes only:** Implement fixes only for defects discovered and reported by testers.
- [ ] **Verification & rebuild:** For every fix, run the full test suite (`bash tests/all.sh`), rebuild the package (`bash tools/build-package.sh`), increment/stamp the new `KIT_VERSION`, and record in the contribution which kit version produced it.

## Withdrawal

- [ ] **Delete records:** Remove the tester's contribution `.jsonl` file from `data/contributions/`, their descriptor files from `tests/real-descriptors/`, `tests/webusb-fixtures/`, and `bench-kit/descriptors/`. Withdrawal means every directory a descriptor can reach.
- [ ] **Rebuild & commit:** Run `python3 data/merge.py` and commit the updated matrix.
- [ ] **Purge uploads:** Permanently delete the tester's form response and uploaded files from Google Drive.
