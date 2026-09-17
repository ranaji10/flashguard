# Testing Runbook

*Organiser runbook for tester invitations, the hackerspace evening on 22 September, the remote wave, file intake, and withdrawal.*

---

## Before any invitation goes out

- [ ] **Build package:** Run `bash tools/build-package.sh` and record the generated ZIP archive SHA-256 checksum.
- [ ] **Verify WebUSB offline:** Open `START-HERE.html` from the unzipped package folder by double-clicking in Chrome on a second machine. Open the developer console and check `typeof navigator.usb`. If it evaluates to `"undefined"`, stop and host the page over HTTPS instead of distributing as a zip file.
- [ ] **Check Drive storage:** Verify available free space on the Google Drive account configured behind the intake form.
- [ ] **Dry-run submission:** Send one test submission through the Google form and confirm that the upload lands in Drive and the response is logged.

## The hackerspace evening, 22 September

- [ ] **Print STOP-LIST:** Print copies of `bench-kit/STOP-LIST.txt` and keep them visible at testing stations.
- [ ] **Unique handles:** Ensure each participant chooses and uses their own distinct handle.
- [ ] **Kit commands only:** Enforce that nobody runs any command or tool outside the provided kit.
- [ ] **No verdicts:** Never disclose or communicate a safety verdict to any tester (Tier A data collection only).
- [ ] **Record failures honestly:** If a device will not connect, record it as not connecting; never retry with unauthorized tools or commands.

## Remote testers

- [ ] **Send kit:** Send one email per tester containing the ZIP package and `participation-note.md`.
- [ ] **Support policy:** If a tester replies that "nothing was detected", direct them to the `01-detect.sh` terminal output, port, and cable troubleshooting advice; never suggest alternative tools or unauthorized scripts.

## When a file comes back

- [ ] **Download:** Download the returned session export JSON file from Google Drive.
- [ ] **Dry-run intake:** Run `python3 tools/intake.py <path/to/flashguard-handle-timestamp.json>` and inspect the verification report.
- [ ] **Commit data:** Run `python3 tools/intake.py <path/to/flashguard-handle-timestamp.json> --write`, followed by `python3 data/merge.py` and `python3 data/coverage.py`. Commit the new contribution and descriptor files.
- [ ] **Monitor storage:** Check Google Drive free space when the fifth file is received.

## Changes during testing

- [ ] **Defect fixes only:** Implement fixes only for defects discovered and reported by testers.
- [ ] **Verification & rebuild:** For every fix, run the full test suite (`bash tests/all.sh`), rebuild the package (`bash tools/build-package.sh`), increment/stamp the new `KIT_VERSION`, and record in the contribution which kit version produced it.

## Withdrawal

- [ ] **Delete records:** Remove the tester's contribution `.jsonl` file from `data/contributions/` and their descriptor files from `tests/real-descriptors/`.
- [ ] **Rebuild & commit:** Run `python3 data/merge.py` and commit the updated matrix.
- [ ] **Purge uploads:** Permanently delete the tester's form response and uploaded files from Google Drive.
