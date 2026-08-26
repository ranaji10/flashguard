# Device matrix record schema

`schema_version: 0.2`  ·  One JSON object per line in `device-matrix.jsonl`.

Changed from 0.1 after the first bench run raised three defects: blank was
indistinguishable from unknown, one physical device could present in two USB classes
with no way to record both, and nothing in the schema itself told a tester what must
never go in it.

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
  "device_mode": "default",

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

## Coverage

    python3 coverage.py

Reads `device-matrix.jsonl` and prints what the dataset actually covers: device
count, classes, chipset families, partition schemes, positives against negatives,
and verifier agreement. This is the project's real state of validation, and the only
index worth maintaining.
