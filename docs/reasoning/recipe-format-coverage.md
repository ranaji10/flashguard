# v0.1 recipe-format coverage

**Status: measurement record.** This is a field census, not a conclusion about the
verifier and not a format proposal. No recipe, verifier, or upstream file was changed.

## Measurement basis

The measurement uses the same active-record denominators as
`docs/reasoning/prerequisite-survey.md`: 90 OpenAndroidInstaller YAML configs, 556
postmarketOS `deviceinfo` files, and 737 LineageOS device metadata YAML files, for
**1,383 records total**. The checkouts were already present under `../library/upstream/`
and were not re-cloned.

| Source | Checkout commit |
|---|---|
| OpenAndroidInstaller | `6a8a1239e33314333e24dc84b11d4dc1730a9c97` |
| postmarketOS pmaports | `817ed870e92a64963d926354fb74c75090811fcc` |
| LineageOS lineage_wiki | `fc68abe69154ed3b88ea200f8b87dea91f84811d` |

The runner is `python3 data/recipe_format_coverage.py`. It reuses
`data/prerequisite_survey.py` for identity and partition classification. A count means
the source record carries the fact needed to populate that recipe field without
guessing. `schema_version`, `recipe_id`, and `source.device_facts_from` are mechanical
wrapper fields; `source.consulted` and all authorship/verdict fields require a human
or a measurement date and therefore count zero as upstream-carried facts.

For arrays, a record counts only when it carries the relevant structure. A UI image,
device icon, kernel description, or flash-target name is not a provisioning asset.
An operation can be structurally described without its asset identity; that is why
operation fields are reported separately.

## Fields the sources can populate

Counts are `count / denominator` on every line. `structured` and `prose only` are
shown where the survey classifier has those categories; recipe-field coverage uses
the structured count because the recipe schema needs machine-readable input.

### OpenAndroidInstaller, denominator 90

| v0.1 field | Structured / available | Prose only | Absent / unavailable |
|---|---:|---:|---:|
| `schema_version` | 90 / 90 | 0 / 90 | 0 / 90 |
| `recipe_id` | 90 / 90 | 0 / 90 | 0 / 90 |
| `source.device_facts_from` | 90 / 90 | 0 / 90 | 0 / 90 |
| `source.consulted` | 0 / 90 | 0 / 90 | 90 / 90 |
| `source.authored` | 0 / 90 | 0 / 90 | 90 / 90 |
| `source.verdict_reason` | 0 / 90 | 0 / 90 | 90 / 90 |
| `human_assessment` | 0 / 90 | 0 / 90 | 90 / 90 |
| `expected_verdict` | 0 / 90 | 0 / 90 | 90 / 90 |
| `expected_verdict_reason` | 0 / 90 | 0 / 90 | 90 / 90 |
| `verdict_gap_reason` | 0 / 90 | 0 / 90 | 90 / 90 |
| `target.product_device` | 90 / 90 | 0 / 90 | 0 / 90 |
| `target.variant` | 90 / 90 | 0 / 90 | 0 / 90 |
| `target.partition_scheme` | 90 / 90 | 0 / 90 | 0 / 90 |
| `assets` | 0 / 90 | 0 / 90 | 90 / 90 |
| `assets.asset_id` | 0 / 90 | 0 / 90 | 90 / 90 |
| `assets.role` | 0 / 90 | 0 / 90 | 90 / 90 |
| `assets.product_device` | 0 / 90 | 0 / 90 | 90 / 90 |
| `assets.variant` | 0 / 90 | 0 / 90 | 90 / 90 |
| `operations` / `operations.kind` | 90 / 90 | 0 / 90 | 0 / 90 |
| `operations.partition` | 15 / 90 | 0 / 90 | 75 / 90 |
| `operations.asset_id` | 0 / 90 | 0 / 90 | 90 / 90 |

### postmarketOS, denominator 556

| v0.1 field | Structured / available | Prose only | Absent / unavailable |
|---|---:|---:|---:|
| `schema_version` | 556 / 556 | 0 / 556 | 0 / 556 |
| `recipe_id` | 556 / 556 | 0 / 556 | 0 / 556 |
| `source.device_facts_from` | 556 / 556 | 0 / 556 | 0 / 556 |
| `source.consulted` | 0 / 556 | 0 / 556 | 556 / 556 |
| `source.authored` | 0 / 556 | 0 / 556 | 556 / 556 |
| `source.verdict_reason` | 0 / 556 | 0 / 556 | 556 / 556 |
| `human_assessment` | 0 / 556 | 0 / 556 | 556 / 556 |
| `expected_verdict` | 0 / 556 | 0 / 556 | 556 / 556 |
| `expected_verdict_reason` | 0 / 556 | 0 / 556 | 556 / 556 |
| `verdict_gap_reason` | 0 / 556 | 0 / 556 | 556 / 556 |
| `target.product_device` | 556 / 556 | 0 / 556 | 0 / 556 |
| `target.variant` | 0 / 556 | 0 / 556 | 556 / 556 |
| `target.partition_scheme` | 26 / 556 | 0 / 556 | 530 / 556 |
| `assets` | 0 / 556 | 0 / 556 | 556 / 556 |
| `assets.asset_id` | 0 / 556 | 0 / 556 | 556 / 556 |
| `assets.role` | 0 / 556 | 0 / 556 | 556 / 556 |
| `assets.product_device` | 0 / 556 | 0 / 556 | 556 / 556 |
| `assets.variant` | 0 / 556 | 0 / 556 | 556 / 556 |
| `operations` / `operations.kind` | 552 / 556 | 0 / 556 | 4 / 556 |
| `operations.partition` | 26 / 556 | 0 / 556 | 530 / 556 |
| `operations.asset_id` | 0 / 556 | 0 / 556 | 556 / 556 |

### LineageOS metadata, denominator 737

| v0.1 field | Structured / available | Prose only | Absent / unavailable |
|---|---:|---:|---:|
| `schema_version` | 737 / 737 | 0 / 737 | 0 / 737 |
| `recipe_id` | 737 / 737 | 0 / 737 | 0 / 737 |
| `source.device_facts_from` | 737 / 737 | 0 / 737 | 0 / 737 |
| `source.consulted` | 0 / 737 | 0 / 737 | 737 / 737 |
| `source.authored` | 0 / 737 | 0 / 737 | 737 / 737 |
| `source.verdict_reason` | 0 / 737 | 0 / 737 | 737 / 737 |
| `human_assessment` | 0 / 737 | 0 / 737 | 737 / 737 |
| `expected_verdict` | 0 / 737 | 0 / 737 | 737 / 737 |
| `expected_verdict_reason` | 0 / 737 | 0 / 737 | 737 / 737 |
| `verdict_gap_reason` | 0 / 737 | 0 / 737 | 737 / 737 |
| `target.product_device` | 737 / 737 | 0 / 737 | 0 / 737 |
| `target.variant` | 220 / 737 | 0 / 737 | 517 / 737 |
| `target.partition_scheme` | 281 / 737 | 0 / 737 | 456 / 737 |
| `assets` | 0 / 737 | 0 / 737 | 737 / 737 |
| `assets.asset_id` | 0 / 737 | 0 / 737 | 737 / 737 |
| `assets.role` | 0 / 737 | 0 / 737 | 737 / 737 |
| `assets.product_device` | 0 / 737 | 0 / 737 | 737 / 737 |
| `assets.variant` | 0 / 737 | 0 / 737 | 737 / 737 |
| `operations` / `operations.kind` | 737 / 737 | 0 / 737 | 0 / 737 |
| `operations.partition` | 271 / 737 | 0 / 737 | 466 / 737 |
| `operations.asset_id` | 0 / 737 | 0 / 737 | 737 / 737 |

The Lineage operation counts reflect the shared structured install template plus the
metadata branches, not rendered-page output. The template-aware procedure pass remains
separate from this metadata census as recorded in `prerequisite-survey.md`.

## Fields reliably carried with no v0.1 place

The sources carry structured fields that do not map to any v0.1 recipe field. Counts
below use the same denominators and name the source field rather than reproducing its
contents.

| Project | Source field(s) | Records carrying it |
|---|---|---:|
| OpenAndroidInstaller | `requirements.android` | 48 / 90 |
| OpenAndroidInstaller | `additional_steps` | 15 / 90 |
| OpenAndroidInstaller | `supported_device_codes` aliases beyond the target identity | 84 / 90 |
| OpenAndroidInstaller | typed unlock/reboot/confirmation workflow steps | 90 / 90 |
| postmarketOS | `deviceinfo_flash_method` | 552 / 556 |
| postmarketOS | `deviceinfo_kernel_cmdline` | 398 / 556 |
| postmarketOS | `deviceinfo_arch` | 555 / 556 |
| postmarketOS | `deviceinfo_dtb` | 199 / 556 |
| LineageOS | `custom_unlock_cmd` | 103 / 737 |
| LineageOS | `before_install` firmware prerequisite | 401 / 737 |
| LineageOS | `before_recovery_install` prerequisite and partition list | 271 / 737 |
| LineageOS | `install_method` | 737 / 737 |
| LineageOS | `uses_twrp` | 184 / 737 |
| LineageOS | `current_branch` | 737 / 737 |

These are field-presence measurements only. No conclusion is drawn from them here.

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
