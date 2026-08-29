# Device matrix record schema

`schema_version: 0.3`  ·  One JSON object per line in `device-matrix.jsonl`.

Changed from 0.1 after the first bench run raised three defects: blank was
indistinguishable from unknown, one physical device could present in two USB classes
with no way to record both, and nothing in the schema itself told a tester what must
never go in it.

Changed again to 0.3 the same day, after the merge step was written and immediately
showed that thirteen records from five physical devices looked like **twelve distinct
devices**. Nothing in 0.2 tied repeat captures of one phone together. Added
`device_local_id`, `usb_mode` and `descriptor_file`.

---

## Never record these. Any field, including `notes`.

    serial number      IMEI       IMSI          MAC address
    Android ID         ICCID      phone number  account identifiers

This dataset is published openly. `bench-kit/scripts/` query an explicit allowlist of
device properties so these cannot be collected by accident. **Do not replace those
scripts with a `getprop` dump or a raw `fastboot getvar all` paste.** Both print the
serial.

Raw command output belongs in `raw/`, which is gitignored, and is deleted once the
record is written.

---

## Three ways a field can have no value

The 0.1 schema could not tell these apart, which made the data unusable for exactly
the question it exists to answer.

| Value | Means | Example |
|---|---|---|
| `"not_applicable"` | This field cannot apply to this class of device | `bootloader_state` on a camera |
| `"unknown"` | It applies, and could not be established read-only | `bootloader_unlockable` on most Androids |
| an actual value | Observed | `"locked"` |

A missing key is a defect, not a third kind of absence. Write the sentinel.

---

## Record

```json
{
  "schema_version": "0.2",
  "record_id": "uuid",
  "tester": "handle-or-initials",
  "consent_ack": true,
  "date": "2026-08-26",

  "host": {
    "os": "Ubuntu 24.04 live / Windows 10 / macOS 14",
    "method": "linux-live | windows-chrome | other",
    "browser": "not_applicable | Chrome 128 | Edge"
  },

  "connection": "USB-C | USB-A",
  "cable_notes": "",

  "reported_device": "what the tester says it is: make, model, year",
  "device_local_id": "samsung-galaxy-a5",
  "identity_source": "tester_identified | unidentified",
  "device_mode": "default",
  "usb_mode": "file transfer (MTP)",
  "descriptor_file": "04e8-6860-20260829-183012.desc",

  "detected": {
    "usb_vendor_id": "0x____",
    "usb_product_id": "0x____",
    "device_class": "mass_storage | ptp_camera | mtp | adb | fastboot | ios | unknown",
    "usb_interface_class": "0x__",

    "android": {
      "product_model": "not_applicable",
      "product_device": "not_applicable",
      "manufacturer": "not_applicable",
      "board_platform": "not_applicable",
      "hardware": "not_applicable",
      "android_version": "not_applicable",
      "sdk": "not_applicable",
      "security_patch": "not_applicable",
      "build_fingerprint": "not_applicable",
      "partition_scheme": "not_applicable",
      "slot_suffix": "not_applicable",
      "bootloader_state": "not_applicable",
      "verified_boot_state": "not_applicable",
      "bootloader_unlockable": "not_applicable"
    }
  },

  "classification_correct": true,
  "classifier_confidence": null,

  "verifier_runs": [
    { "recipe_id": "good-01", "expected": "safe", "verdict": "safe", "match": true }
  ],

  "related_records": [],
  "duration_minutes": null,
  "notes": ""
}
```

---

## Field notes

**`identity_source`** New in 0.2, added 29 Aug after the first bench run. `tester_identified`
means a human who knows the device named it independently, before seeing any scan output.
`unidentified` means nobody could say what it was. **This is the ground-truth flag, and it decides
whether a record can be used to validate the classifier at all.**

A record whose identity came from agreeing with the tool cannot validate the tool: that is circular,
and it silently launders a classifier error into the dataset as fact. On the first bench run six of
thirteen records carried no make or model, because the interface only asked when the tester
disagreed with the scan. The console now asks before running the scan, every time.

`coverage.py` should count only `tester_identified` records toward classifier accuracy.
`unidentified` records still belong in the matrix: a device nobody can name is a real and common
condition, and the tool has to behave sensibly on one.

**`device_local_id`** New in 0.3, and the field that makes the dataset countable.
One physical phone reports a **different USB product ID in every mode**. The Samsung A5
on the first bench run gave `0x6860`, `0x6866`, `0x686c` and `0x6845` across four
captures, with three different first-interface classes. Keyed on vendor:product, that is
four phones. Keyed on `device_local_id`, it is one phone observed four times, which is
what it is.

The value is a slug the tester chooses once, scoped to that tester: `samsung-galaxy-a5`.
`merge.py` namespaces it as `<tester>/<device_local_id>`, so two testers can both have a
`samsung-galaxy-a5` without colliding. **It is never derived from a serial number**, and
it does not need to be globally unique or meaningful to anyone else — only stable for one
person across one drawer.

When it is missing, `merge.py` falls back to `reported_device`, then to vendor:product,
and reports how many records fell through. A record keyed on vendor:product cannot
distinguish two identical devices owned by the same tester.

The console offers previously-captured devices as buttons on the identify screen, so a
re-scan binds to the existing device rather than creating a new one.

**`usb_mode`** New in 0.3. Which USB mode the *owner had selected*, in the phone's own
words: `charging only`, `file transfer (MTP)`, `photo transfer (PTP)`, `MIDI`,
`USB tethering`, `mass storage`, `not applicable`, `do not know`.

This is not a fingerprinting field, and that is the point. Fingerprinting is settled by
adb once debugging is on; the mode barely matters there. `usb_mode` exists because **the
real tool's input is whatever mode the device happens to be in when a stranger plugs it
in**, and most phones default to charging only. The verifier's job in that state is not
to guess — it is to abstain and tell the person which setting to change. Data on which
modes produce which presentation is what makes that instruction correct rather than
folklore.

So: capture each device once in its natural mode. Sweep modes only when adb is *not*
available and the device offers a choice — a camera with PTP versus card-reader, a phone
too old for developer options. Sweeping modes on an adb-capable phone gathers little.

**`descriptor_file`** New in 0.3. Filename of the saved `lsusb -v` descriptor in
`bench-kit/descriptors/`, with `iSerial` stripped at capture. Every capture is therefore
a replayable test case; see `tests/`. `"not_saved"` if the stick was read-only.

**`device_mode`** New in 0.2. Some devices present as a different USB class depending
on a setting the owner changed long ago and does not remember. A Fuji camera can
appear as PTP or as a card reader. Record one entry per mode, give each a distinct
`device_mode` string, and cross-reference them in `related_records`. This is a real
classifier problem and the dataset has to be able to express it.

**`partition_scheme`** `"A/B"` when `ro.boot.slot_suffix` is non-empty, `"single"`
when it is empty and the device is otherwise readable, `"unknown"` when it could not
be read.

**`bootloader_unlockable`** Almost always `"unknown"`. Whether a bootloader *can* be
unlocked is generally not determinable read-only. Recording `"unknown"` honestly is
the point; guessing here is how a verifier learns to be wrong.

**`classifier_confidence`** `null` until there is a classifier. Do not invent numbers
for hand-made records.

**`duration_minutes`** How long this device actually took. Feeds the completion-rate
analysis, which is a finding about accessibility, not bookkeeping.

**`consent_ack`** The tester confirmed they read `docs/participation-note.md` before
running anything. A record without it is not published.

---

## How many testers' files become one matrix

    data/contributions/rana-2026-08-29.jsonl     as returned, never edited
    data/contributions/priya-2026-09-14.jsonl
    data/contributions/j-doe-2026-09-15.jsonl
              |
              |   python3 data/merge.py
              v
    data/device-matrix.jsonl                     GENERATED. Do not hand-edit.

One file per tester per session. Fifteen people appending to one shared file is a merge
conflict every time and makes withdrawal impossible; one file per submission makes a
withdrawal `rm` plus a rebuild, which is what `participation-note.md` promises.

`merge.py` validates before it writes: rejects records without `consent_ack`, refuses
duplicate `record_id`s, scans every line for IMEI-shaped numbers, MAC addresses and
forbidden field names, groups observations by device, and fills `capture_seq`,
`capture_count` and `related_records` automatically. `--check` validates and writes
nothing, for use before accepting a contribution.

A tester returns one JSONL file and, if they can, the `descriptors/` folder. Nothing
else. The descriptors are what let a classifier change be re-tested against their
devices without asking them to plug anything in again.

## Coverage

    python3 coverage.py

Reads `device-matrix.jsonl` and prints what the dataset actually covers: device
count, classes, chipset families, partition schemes, positives against negatives,
and verifier agreement. This is the project's real state of validation, and the only
index worth maintaining.
