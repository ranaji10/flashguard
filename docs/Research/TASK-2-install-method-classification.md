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
