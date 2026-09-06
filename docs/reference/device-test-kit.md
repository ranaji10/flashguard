# Device test kit — detect · fingerprint · verify (read-only)

A repeatable, low-risk way to run the prototype on real devices and produce comparable
records that become both the grant's validation evidence and the research ground truth.

**Reference document.** The tester-facing one-pager is `../bench-kit/protocol.md`. The
guided version that runs on the bench machine is `../bench-kit/START-HERE.html`.

---

## Safety tiering — read this first

| Tier | Actions | Risk | Who / when |
|---|---|---|---|
| **A — Detect & fingerprint** | Enumerate USB devices, classify, read Android properties read-only | **None**, nothing writes | Everyone, any device |
| **B — Verify in simulation** | Run candidate recipes through the verifier against the detected state | **None**, nothing executes on hardware | Everyone |
| **C — Actual flash** | Execute a recipe on a device | **Can permanently brick** | Opt-in ONLY, on a device the owner accepts losing, with **written** consent. **Not required for the grant, and not before the grant decision.** |

The prototype and the tester programme run at **Tier A + B only.**

Tier C, if it ever happens, needs a real written consent instrument. A logged verbal yes
is not one.

---

## The recommended tester path is Linux, not Windows <!-- v0.2 -->

The bench machine boots a Linux live image with device rules already in place.

This is not preference. On Windows, WebUSB and fastboot require installing a WinUSB driver
with a tool like Zadig, and that step is where a volunteer with a spare hour decides this
is not their evening. It is doubly unfortunate because driver-swapping *feels* dangerous
even though Tier A writes nothing. The live image removes the problem rather than
documenting it.

The Windows plus Chromium route is kept as a fallback and its friction is still logged,
because smoothing it is a legitimate deliverable. It is no longer the default first
experience.

> One warning if a tester does use Windows: Zadig replaces the driver for whichever device
> is selected in its dropdown. Selecting the wrong entry breaks that device on that machine
> until the driver is rolled back. Only ever select the Android device in fastboot mode.

---

## Never record these <!-- v0.2 -->

    serial number   IMEI   IMSI   MAC address   Android ID   ICCID   phone number

The matrix is published as open data. `bench-kit/scripts/` query an **explicit allowlist**
of device properties one at a time, rather than dumping state, precisely so these cannot
be collected by accident. Both `adb devices` and `fastboot getvar all` print the device
serial.

**Do not simplify the scripts into a `getprop` dump.** Raw output goes in `raw/`, which is
gitignored, and is deleted once the scrubbed record is written.

Every tester sees `participation-note.md` before running anything. A record without
`consent_ack` is not published.

---

## Record schema

Now maintained in `../data/schema.md` at `schema_version: 0.2`, with the exclusion list,
the `not_applicable` versus `unknown` distinction, and `device_mode` for devices that
present differently depending on a setting.

Records go one per line in `../data/device-matrix.jsonl`. Coverage:

    cd ../data && python3 coverage.py

---

## Tester protocol (Tier A + B)

1. Boot the bench machine from the Linux live image. *(Fallback: Chromium on Windows, plus
   the WinUSB driver step.)*
2. Open `bench-kit/START-HERE.html`. It walks through the rest offline.
3. Run `bash 00-setup.sh` once. Installs read-only tools, takes the USB baseline.
4. Plug in one device. Run `bash 01-detect.sh`. Confirm or correct the classification.
5. If it is an Android in adb mode, run `bash 02-android.sh` for the allowlisted
   fingerprint. Optionally `bash 03-fastboot.sh` for the bootloader-side view.
6. Build the record in the page's record builder. Save to the kit stick.
7. Unplug, next device.

**No flashing.** If any instruction says otherwise, it is not this protocol.

---

## Recipe corpus

Maintained in `../data/recipes/`. Each recipe carries an `expected` verdict so precision
and recall are measurable. The build fails on a single **false safe**. Abstention rate is
reported alongside so a verifier that refuses everything cannot look successful.

Recipes are not devices, and recipes are published: OpenAndroidInstaller's 88 per-device
configurations, LineageOS install instructions, the postmarketOS device matrix. The corpus
can reach the hundreds without owning the hardware. Physical devices are reserved for the
one thing only hardware gives: the read-only fingerprint.

---

## The seed devices <!-- v0.2 -->

Reference entries showing testers what "done" looks like.

| Device | Expected class | Role in the test set |
|---|---|---|
| Acer (2012) | **host machine** | Runs the bench. Itself an out-of-support device, so also a future Linux-repurpose target. Not a flash target. |
| iPhone 8 | `ios` | Correct-negative. Must be flagged **unsupported for flashing**. |
| Kobo reader | `mass_storage` or `mtp` | Correct-negative. Which one it reports is a finding, record it. |
| Fuji X-T30 | `ptp_camera` | Correct-negative, **and record it twice**. See below. |
| Fuji X-T20 | `ptp_camera` | Correct-negative. *(Previously written as "TX20". Confirm from the body.)* |
| USB sticks / HDDs | `mass_storage` | Correct-negatives. Enumeration must not confuse storage for a target. |
| **Unknown Android** | `adb` or `fastboot` | **The one live positive.** Read-only fingerprint, identify make and model, run the verifier against its real state. |

**The Fuji two-mode case.** The same physical camera presents as a different USB class
depending on a menu setting its owner changed months ago and does not remember. Record one
entry per mode with distinct `device_mode` values, cross-referenced in `related_records`.
This is a genuine classifier problem with no clean solution and it is direct evidence for
`cannot-verify` being a real verdict rather than a failure state.

**On the balance of the seed set.** One live positive against six negatives is not a
validated verifier, and the proposal no longer claims it is. The negatives prove the
classifier does not produce false positives, which for a safety tool matters as much. Scale
comes from the recipe corpus and the tester network, not from this table.

---

## After the pilot, before fielding it

The seed run is a pilot of a research instrument. Answer these in writing:

1. **What had to be invented?** Every value the schema did not anticipate is a defect found
   before it reached twenty strangers.
2. **Did `not_applicable` and `unknown` stay distinct in practice?** If you hesitated over
   which to pick, the schema is still wrong.
3. **How long did each device actually take?** This decides whether a volunteer finishes,
   and it is what the ask should honestly claim.
