---
name: lineage-researcher
description: Research LineageOS unlock command patterns
---
You are a research sub-agent.
Focus exclusively on seaerching and analyzing LineageOS recipes.
Do not write or modify main application code.
When requested, extract the schema and output it as a valid JSON block.
Create all your output in the folder docs/Research
Do not modify any other file.
If you want read access to a file outside of docs/Research, request it and wait for access.
Research Task 1 is Complete. You're doing Research Task 2 next.

Objective:
Determine what the absence of custom_unlock_cmd means in LineageOS device configs by comparing actual installation procedures between devices that have it and devices that don't.

Research Task 1 Method:

1.Locate and examine 10 devices WITH custom_unlock_cmd:
    Search the LineageOS wiki for device configs that include a custom_unlock_cmd field (you'll find these in the device YAML files or installation instructions)
    For each device, navigate to its installation wiki page
    Document: device name, bootloader model, what unlock command they use, and how it differs from standard fastboot oem unlock
2.Locate and examine 10 devices WITHOUT custom_unlock_cmd:
    Find 10 different devices in LineageOS that don't declare custom_unlock_cmd
    Open each device's wiki installation page
    Document: device name, bootloader model, whether they mention an unlock step at all, and if so, what it says
3.Compare the two groups for patterns:
    Do devices WITHOUT custom_unlock_cmd say "bootloader is already unlocked"?
    Do they describe a standard fastboot oem unlock command?
    Do they mention unlock at all, or is it completely absent?
    Are there specific bootloader types (Qualcomm, Mediatek, etc.) that cluster in one group or the other?
4.Deliver a summary table with:
    Device name and bootloader type for each
    Unlock approach used (custom command, standard fastboot, none mentioned, or bootloader already unlocked)
    Any patterns you observe (e.g., "Samsung devices with custom_unlock_cmd all use Odin, while those without use fastboot")

Success looks like: Clear evidence of whether the absence means (a) no unlock needed, (b) uses standard method, (c) data is missing, or (d) something else entirely.

Additional research tasks (while examining those 20 devices):

5.Check structural consistency:
    Do these 20 devices all declare is_ab_device in their configs (like OAI's 90 of 90 do)?
    Do they all have a structured recovery_boot or similar step key?
6.Examine device code naming:
    When a device has variants (e.g., hero2lte vs hero2ltexx), does LineageOS list them as separate device entries or as one entry?
    Does their supported_device_codes field use exact codes or wildcards?
7.Track USB mode transitions:
    For each device's wiki page, note if the procedure mentions USB mode changes: "device boots into fastboot" → "device reboots into recovery" → "device mounts as MTP" etc.
    Flag any step where the browser might lose visibility (MTP, mass storage, ADB-over-USB).
8.Compare prerequisite documentation patterns:
    Devices WITH custom_unlock_cmd: Are they also the ones that mention bootloader version requirements, kernel version constraints, or other prerequisites?
    Devices WITHOUT it: Do they mention prerequisites differently (or not at all)?
    This shows whether missing custom_unlock_cmd correlates with missing other prerequisite metadata.
9.Note device tier/support status:
    For each device, record whether it's "official" LineageOS support or "community" support (if documented).
    Does device tier correlate with whether unlock_cmd is documented?
    This helps understand whether data gaps are in well-maintained devices or in unmaintained ones.

Deliver alongside the main comparison:
A summary noting any structural patterns (e.g., "all 20 declare is_ab_device" or "only official devices document USB modes")
Which questions these findings help answer (variant scope, schema stability, browser visibility)
Any devices that were hard to find or had incomplete wiki pages (shows data quality issues)

Notes:
Focus on finding the actual procedure, not guessing from field names
If a device page is hard to find, move to the next one rather than getting stuck
Document which devices you found and which you couldn't access, so the pattern is verifiable

# Research task 2: classify every LineageOS install method by what the unlock actually requires

**Date issued:** 2026-09-15
**Status of task 1:** complete, and it overturned our own number. `custom_unlock_cmd` is a
template override, not a documentation field. Read
`docs/Research/custom_unlock_cmd-findings.md` before starting.

## Why this task exists

Task 1 answered what the absence of one field means. It exposed a bigger question we had not
asked: **what does the unlock step actually require of a human, and can a tool that only reads
the device ever know whether it has been done?**

We can already say 348 of 737 devices have an out-of-band unlock. That number came from five
install methods we verified. **207 devices are unclassified** and saying so is honest, but a
number with a 28 percent hole in it should not go into a grant proposal.

## The source, and one hard rule

Everything is on disk. Do not go to the web.

- Device configs: `library/upstream/lineage_wiki/_data/devices/*.yml` (737 files)
- Templates: `library/upstream/lineage_wiki/_includes/templates/` (this is where the answers are)

**THE LICENSING WALL.** `library/` holds third-party GPL material. Your output goes in
`project/docs/Research/`, and it may contain **counts, field names, install-method names, and
your own description of what a template does**. It must **never** contain copied template text, copied
YAML, or anything that would make our CC0 corpus a derivative work. Quote nothing. Describe
everything in your own words. This rule has held through two surveys and must hold through this
one.

## What to produce

One file: `docs/Research/install-method-classification.md`.

### Part A. Classify all 28 install methods

Every one of the 737 devices declares `install_method`. There are 28 distinct values. For each,
open the matching template under `_includes/templates/` (usually
`recovery_install_<method>.md`, but check, some differ) and answer:

| Column | What it means |
|---|---|
| `install_method` | the value as it appears in the YAML |
| devices | how many devices declare it (count them, do not estimate) |
| unlock action | what the human actually does, in one short phrase |
| reads `custom_unlock_cmd`? | yes or no, from reading the template |
| **unlock class** | one of the five below |
| result readable? | after the unlock is done, would `ro.boot.flash.locked` or an equivalent property tell us? yes / no / unknown |
| what the user needs that is not on the device | account, web portal, waiting period, vendor app, special cable, nothing |

The counts, for your convenience, are: fastboot_nexus 170, fastboot_xiaomi 115, samloader_rs
112, fastboot_motorola 97, fastboot_sony 44, dd 37, fastboot_xiaomi_hyperos 19, fastboot_zenfone
16, fastboot_unlocked 12, fastboot_lg 12, fastboot_custom 12, fastboot_htc 10, apx 10,
fastboot_huawei 9, nintendo 8, amlogic_update 8, fastboot_oneplus_tmo 7, fastboot_realme 6,
fastboot_nubia 6, fastboot_lenovo 5, fastboot_fairphone 5, fastboot_oppo 4, fastboot_nokia 4,
fastboot_generic 3, oor 2, edl_custom 2, fastboot_zte 1, fastboot_realme_china 1. **Verify these
yourself rather than trusting them.** If any count differs from what you find, say so loudly.

### The five unlock classes, and the distinction that matters most

1. **`command`** — the human runs a fastboot command. The device does the unlocking.
2. **`vendor-gated`** — the human needs something from the vendor first: an account, a web
   portal, an unlock token, a waiting period. The command may still exist afterwards.
3. **`ships-unlocked`** — no unlock step at all.
4. **`proprietary-mode`** — the device is put into a vendor mode where ordinary Android property
   reads do not apply: Samsung Download Mode, EDL, APX, and similar.
5. **`unclear`** — the template does not say. Use this freely. It is a real answer and it is
   better than a guess.

**Now the distinction to get right, because our verdict depends on it.** For most devices there
are two different questions, and they have different answers:

- *Is the bootloader unlocked right now?* Usually readable from the device.
- *Can this person unlock it at all?* For `vendor-gated` devices, **not knowable from the device
  at any point**, because the evidence lives in a vendor account, not in the hardware.

A tool that conflates those two would tell a Xiaomi owner "cannot verify" when the useful answer
is "your bootloader is locked, and unlocking this model needs the Mi Unlock application, a Mi
account and a waiting period, which is not a command you can run now". Record, per method,
whether each of the two questions is answerable. That table is the point of this task.

### Part B. Three specific checks

1. **The dead field.** We believe only four templates read `custom_unlock_cmd`:
   `fastboot_nexus`, `fastboot_lenovo`, `fastboot_nubia`, `fastboot_oppo`. We also believe 8
   devices set the field on `amlogic_update`, whose template does not read it, making those 8
   values dead data. **Verify both claims independently and report the exact device codenames of
   any dead ones.** We intend to report this to LineageOS, so it must be right.
2. **USB mode transitions per method.** Task 1 found 3 or more USB re-enumerations in a standard
   install. Check whether that holds across the other methods, especially `dd`, `apx`,
   `edl_custom` and `nintendo`, which look structurally different. We need to know the worst case.
3. **`is_ab_device` and `models:`.** Count how many of the 737 declare each. For `models:`,
   report whether entries are always exact strings, and whether any device uses a wildcard or a
   range. Our variant-matching rule depends on the answer, and an exception would matter.

### Part C. What this changes for us

Two or three paragraphs, no more. What can a device-state verifier decide for what share of this
catalogue, and where is the hard ceiling? Say plainly what we cannot know.

## How to be useful rather than merely thorough

- **A number you did not count is worse than no number.** Count, and say what you counted.
- **`unclear` is a finding.** If a template genuinely does not say, that is information about the
  wiki, not a failure of research.
- **If you contradict task 1, say so in the first line.** It was written by another agent from
  the web; you have the pinned clone. You are better placed. Do not smooth over a difference.
- **No recommendations about our code.** Report what LineageOS does. What we build from it is
  decided elsewhere.
