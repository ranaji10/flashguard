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

- [ ] **Download:** Download the returned session export JSON file from Google Drive.
- [ ] **Dry-run intake:** Run `python3 tools/intake.py <path/to/flashguard-handle-timestamp.json>` and inspect the verification report.
- [ ] **Handle refusals (if any):**
  - **PII hit / forbidden field / serial:** Look at the file, do not edit it, ask the tester.
  - **Consent not acknowledged (`consent_ack: false`):** Do not write it, ask the tester.
  - **Pending derivation (`android_derivation: pending`):** Run `python3 tools/derive-pending.py <file>` on the Mac, then run intake on `<file>-derived.json`.
  - **Descriptor filename refused:** Look at the descriptor filename by hand (must be a bare name ending in `.desc`).
  - **Contribution file already exists:** Pass `--session-number 2` (or next sequence) to intake.
  - **The rule under pressure:** Never `--no-verify`, never edit a tester's file to make a check pass. A refused file waits. It does not get fixed at 21:40 with five people in the room.
- [ ] **Commit data:** Run `python3 tools/intake.py <path/to/flashguard-handle-timestamp.json> --write`, followed by `python3 data/merge.py` and `python3 data/coverage.py`. Commit the new contribution and descriptor files.
- [ ] **Monitor storage:** Check Google Drive free space when the fifth file is received.

## Changes during testing

- [ ] **Defect fixes only:** Implement fixes only for defects discovered and reported by testers.
- [ ] **Verification & rebuild:** For every fix, run the full test suite (`bash tests/all.sh`), rebuild the package (`bash tools/build-package.sh`), increment/stamp the new `KIT_VERSION`, and record in the contribution which kit version produced it.

## Withdrawal

- [ ] **Delete records:** Remove the tester's contribution `.jsonl` file from `data/contributions/`, their descriptor files from `tests/real-descriptors/`, `tests/webusb-fixtures/`, and `bench-kit/descriptors/`. Withdrawal means every directory a descriptor can reach.
- [ ] **Rebuild & commit:** Run `python3 data/merge.py` and commit the updated matrix.
- [ ] **Purge uploads:** Permanently delete the tester's form response and uploaded files from Google Drive.
