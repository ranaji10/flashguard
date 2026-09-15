# Upstream prerequisite survey

**Status: measurement record.** This document records the counting definitions and
the observed counts. It does not draw a conclusion about the verifier or propose a
new recipe format.

## Definitions used before counting

### Unit of count

One countable unit is one upstream device configuration file in the source's native
configuration directory. A project-level README, shared include, generated index, or
duplicate alias entry is not counted as a device configuration. The denominator is
the number of units selected by these rules, and is printed for every field.

### Structured prerequisite declaration

A config **declares a prerequisite structurally** when the parsed source data contains
a field, mapping key, list item, or typed operation whose name or value identifies a
required condition or action before provisioning: for example an unlock step,
bootloader-state requirement, recovery prerequisite, or explicit precondition. A
command nested under a typed step counts as structured even when its explanatory
text is prose. The declaration must be represented by data structure, not inferred
from a sentence.

A config **mentions a prerequisite in prose only** when its human-readable text says
that unlocking, an unlocked bootloader, recovery preparation, or another prerequisite
is needed, but no parsed field or typed operation identifies it. A structured
declaration is counted as structured, not also as prose-only, even if it has matching
explanatory text. A config with neither is counted as not at all.

### Partition-scheme declaration

A config **declares a partition scheme structurally** when a parsed field explicitly
states A/B, dynamic, single-slot, or an equivalent partition-layout value. A sentence
that merely names slots or says to copy an inactive slot is prose-only evidence and
does not count as a scheme declaration. If the source has no scheme field and no
unambiguous scheme value, it is counted as not at all.

### Device-identity declaration

A config **declares device identity structurally** when parsed fields identify the
device by codename, model, supported codename alias, or an equivalent device key.
The source filename alone does not count. A prose page that names a device but has
no machine-readable device field is prose-only. Identity is counted independently
of prerequisite and partition fields.

### Source-specific treatment

OpenAndroidInstaller is surveyed as structured YAML under its device-config directory.
postmarketOS is surveyed as `deviceinfo` files in pmaports; shell assignments are
treated as structured fields, while comments and free-text values are prose. LineageOS
metadata is surveyed as the machine-readable YAML under `_data/devices/`, which is why
the results include structural counts for 103 unlock and 281 partition records. The
737 install pages are separately linked to a shared template and per-device metadata;
their template-aware procedure pass is still outstanding, so the metadata counts are
a floor for LineageOS procedure evidence, not the answer for the rendered guides.

## Fixtures and method

The classification function is tested with hand-written, minimal text fixtures under
`tests/survey-fixtures/`. It receives text and returns one record; it performs no
network access and no repository-wide implicit scan. The survey runner is handed one
path at a time and reads only that path.

## Results

Results are added below only after the failing fixture check and the pure survey runner
have been run over the three external checkouts. Counts always include their denominator.

## Measured results

Measured 7 September 2026 from the shallow clones under `../library/upstream/`. The
survey read config text for classification and retained only counts and field classes
in this repository.

### OpenAndroidInstaller

The active config directory contains **90 YAML configs**. The three YAML files under
its `removed/` subdirectory were excluded from this denominator as removed configs.

| Field | Structured | Prose only | Not at all | Denominator |
|---|---:|---:|---:|---:|
| unlock prerequisite | 90 | 0 | 0 | 90 |
| partition scheme | 90 | 0 | 0 | 90 |
| device identity | 90 | 0 | 0 | 90 |

### postmarketOS

The pmaports checkout contains **556 `deviceinfo` files**. Each file is one countable
device configuration under the unit definition above.

| Field | Structured | Prose only | Not at all | Denominator |
|---|---:|---:|---:|---:|
| unlock prerequisite | 0 | 0 | 556 | 556 |
| partition scheme or explicit layout | 26 | 0 | 530 | 556 |
| device identity | 556 | 0 | 0 | 556 |

The 26 structured partition-layout records contain `deviceinfo_partition_type` or
`deviceinfo_super_partitions`. Flash-target names such as
`deviceinfo_flash_fastboot_partition_*` were not counted as partition schemes.

### LineageOS

LineageOS has **737 structured device metadata YAML files** under `_data/devices/`
and **737 install pages** under `pages/install/`. The metadata files are counted as
the mechanically surveyable configuration units below:

| Field | Structured | Prose only | Not at all | Denominator |
|---|---:|---:|---:|---:|
| unlock prerequisite | 103 | 0 | 634 | 737 |
| partition scheme | 281 | 0 | 456 | 737 |
| device identity | 737 | 0 | 0 | 737 |

The install pages are a different source shape: each page includes the shared
structured `templates/device_install.md`, and its `device` front-matter value selects
the corresponding `_data/devices/*.yml` record. The template branches on structured
per-device variables including `custom_unlock_cmd`, `before_install`,
`before_recovery_install`, `install_method`, `is_ab_device`, `uses_twrp`, and recovery
fields. Therefore the procedure shape is mechanically recoverable from the template
and metadata without parsing rendered HTML: unlock/recovery prerequisites, firmware
requirements, partition scheme, install method, and branch-dependent operations can
be enumerated.

The current text-only runner did not implement that template evaluation, so it does
not claim counts for the 737 install-page procedures. This is an implementation gap
in the survey, not evidence that the pages are unsurveyable. The denominator is 737
pages; procedure-field counts remain unreported until a template-aware pass is run.

The survey command was:

```text
python3 data/survey_upstream.py
```

## CORRECTION, 15 September 2026: the 103 of 737 was measuring the wrong thing

Asked LineageOS directly. The answer was "open instructions for devices you see that for and
see for yourself", which was terse and was the right instruction. Doing it, against the pinned
clone, settles it.

`custom_unlock_cmd` is a **template override**, not a documentation field. The install
templates render `fastboot oem unlock` as their `else` branch, so the field is set only when
the correct command DEVIATES from that default. Absence means the standard command applies,
not that data is missing.

So 103 of 737 counts deviations. It never counted documentation.

**What is actually declared: 737 of 737 devices declare `install_method`.** Verified by count
against the pinned clone. The unlock procedure is fully determined by `install_method` plus the
optional override, which means LineageOS declares its unlock procedure structurally for every
device it ships, the same as OpenAndroidInstaller. The ecosystem picture is two complete and
one absent, not one complete, one partial and one absent.

**And the more useful number, which nobody had:**

| | devices | share |
|---|---|---|
| Unlock is OUT-OF-BAND: a vendor portal, account or proprietary mode | 348 | 47% |
| Unlock is the standard fastboot command, 85 of them overridden | 170 | 23% |
| Ships pre-unlocked | 12 | 2% |
| Not yet classified | 207 | 28% |

Out-of-band means `fastboot_xiaomi`, `fastboot_xiaomi_hyperos`, `fastboot_motorola`,
`samloader_rs` and `fastboot_fairphone`, each verified by reading the template. Mi Unlock is a
Windows application tied to an account with a waiting period; Motorola and Fairphone use web
portals; Samsung uses Download Mode with no fastboot unlock at all.

**On roughly half this catalogue, no device-state verifier can ever establish that the unlock
prerequisite is satisfiable**, because the evidence does not live on the device. That is a hard
boundary on what any tool of this kind can decide, it is quantified, and it is a finding rather
than a gap.

**One small thing worth sending back to LineageOS.** Eight devices set `custom_unlock_cmd` on
`install_method: amlogic_update`, and `recovery_install_amlogic_update.md` does not read the
field. Those eight values are set and never rendered. `fastboot_nubia` and `fastboot_lenovo`
do read it, so 95 of the 103 are live and 8 are dead data. Checked by reading the templates.

*Method: `library/upstream/lineage_wiki` at the pinned checkout, `_data/devices/*.yml` and
`_includes/templates/recovery_install_*.md`. Full working in `docs/Research/custom_unlock_cmd-findings.md`.*
