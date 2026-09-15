# OpenAndroidInstaller Config Structure Analysis

**Date:** 2026-09-15
**Source:** `openandroidinstaller-dev/openandroidinstaller` on GitHub, branch `main`
**Configs examined in full:** 43 of 93 active YAML files (plus `removed/` directory with 3 files)
**Schema source:** `openandroidinstaller/installer_config.py` (read in full)
**Licensing:** No YAML text reproduced verbatim. All descriptions are original.

---

## Q1 — supported_device_codes scope: exact or family-level?

**Conclusion: variant-level exact strings, not family patterns. Zero wildcards.**

Every entry in every `supported_device_codes` list is a discrete exact string. No glob
characters (`*`, `?`), no regex, no ranges. The code in `installer_config.py` confirms this:
the lookup does a plain `device_code in supported_device_codes` membership test, which
requires an exact string match.

### Evidence from 43 configs examined

| Config | device_code | supported_device_codes (all entries) | Variants covered |
|---|---|---|---|
| hero2lte | hero2lte | hero2lte, hero2ltebmc, hero2lteskt, hero2ltektt, hero2ltelgt, hero2ltexx | 6 — Samsung Galaxy S7 Edge regional variants |
| herolte | herolte | herolte, heroltexx, heroltebmc, herolteskt, heroltektt, heroltelgt | 6 — Samsung Galaxy S7 regional variants |
| a5xelte | a5xelte | a5xelte, a5xeltexx, a5xelteub, a5xeltedo | 4 — Samsung A5 2016 regional variants |
| a3y17lte | a3y17lte | a3y17lte, a3y17ltexc, a3y17ltexx, a3y17ltelk | 4 — Samsung A3 2017 regional variants |
| a5y17lte | a5y17lte | a5y17lte, a5y17ltecan, a5y17ltexx | 3 — Samsung A5 2017 regional variants |
| a7xelte | a7xelte | a7xelte, a7xeltexx, a7xelteub, a7xeltedo | 4 — Samsung A7 2016 regional variants |
| a7y17lte | a7y17lte | a7y17lte, a7y17ltexx | 2 — Samsung A7 2017 regional variants |
| klte | klte | klte, klteacg, kltecan, kltetmo, klteub, klteusc, kltevzw, kltexx | 8 — Samsung S5 US carrier + regional |
| zerofltexx | zerofltexx | zerofltexx, zeroflte | 2 — Samsung S6 |
| zeroltexx | zeroltexx | zeroltexx, zerolte | 2 — Samsung S6 Edge |
| jfltexx | jfltexx | jfltexx, jflte, jfltetmo, jfltecan, jgedlte | 5 — Samsung S4 (Qualcomm) regional/carrier |
| dreamlte | dreamlte | dreamlte | 1 — Samsung S8 (single) |
| starlte | starlte | starlte | 1 — Samsung S9 (single) |
| crownlte | crownlte | crownlte | 1 — Samsung Note 9 (single) |
| greatlte | greatlte | greatlte | 1 — Samsung Note 8 (single) |
| a72q | a72q | a72q | 1 — Samsung A72 (single) |
| alioth | alioth | alioth, aliothin | 2 — Xiaomi Redmi K40/Mi11X/POCO F3 (Indian variant) |
| miatoll | miatoll | miatoll, gram, curtana, excalibur, joyeuse | 5 — Xiaomi Redmi Note 9S family (5 board variants) |
| Mi439 | Mi439 | Mi439, mi439, pine, olive, olivelite, olivewood, olives | 7 — Xiaomi Redmi 7A/8/8A/8A Dual (distinct hardware) |
| lavender | lavender | lavender | 1 — Xiaomi Redmi Note 7 |
| ginkgo | ginkgo | ginkgo, willow | 2 — Xiaomi Redmi Note 8/8T |
| surya | surya | surya, karna | 2 — Poco X3 / X3 NFC |
| vayu | vayu | vayu, bhima | 2 — Poco X3 Pro |
| raphael | raphael | raphael, raphaelin | 2 — Mi 9T Pro / Redmi K20 Pro |
| cupid | cupid | cupid | 1 — Xiaomi 12 |
| davinci (not read) | — | — | — |
| FP2 | FP2 | FP2 | 1 — Fairphone 2 |
| FP3 | FP3 | FP3 | 1 — Fairphone 3 |
| FP4 | FP4 | FP4 | 1 — Fairphone 4 |
| kirin | kirin | kirin | 1 — Sony Xperia 10 |
| avicii | avicii | avicii, Nord | 2 — OnePlus Nord (codename + marketing name) |
| enchilada | enchilada | enchilada, OnePlus6 | 2 — OnePlus 6 (codename + marketing name) |
| guacamole | guacamole | guacamole, OnePlus7Pro | 2 — OnePlus 7 Pro |
| guacamoleb | guacamoleb | guacamoleb, OnePlus7 | 2 — OnePlus 7 |
| hotdog | hotdog | hotdog, OnePlus7TPro | 2 — OnePlus 7T Pro |
| hotdogb | hotdogb | hotdogb, OnePlus7T | 2 — OnePlus 7T |
| bacon | bacon | bacon, A0001 | 2 — OnePlus One (codename + model number) |
| oneplus3 | oneplus3 | OnePlus3, oneplus3, OnePlus3T, oneplus3t | 4 — OnePlus 3 AND 3T in one config |
| blueline | blueline | blueline | 1 — Pixel 3 |
| crosshatch | crosshatch | crosshatch | 1 — Pixel 3 XL |
| redfin | redfin | redfin | 1 — Pixel 5 |
| sargo | sargo | sargo | 1 — Pixel 3a |
| sunfish | sunfish | sunfish | 1 — Pixel 4a |
| flame | flame | flame | 1 — Pixel 4 |
| coral | coral | coral | 1 — Pixel 4 XL |
| barbet | barbet | barbet | 1 — Pixel 5a |
| bonito | bonito | bonito | 1 — Pixel 3a XL |
| taimen | taimen | taimen | 1 — Pixel 2 XL |
| walleye | walleye | walleye | 1 — Pixel 2 |

### Patterns observed

**Pattern A — Regional/carrier variants in one list.** The Samsung A-series and Galaxy S-series
configs (a5xelte, a7xelte, herolte, hero2lte, klte, jfltexx) list all regional and carrier
suffixes explicitly. `klte` has 8 entries covering the US carrier variants (TMO, USC, VZW, ACG)
alongside international variants. Every entry is an exact string; the config is matched to
whichever exact code the device reports.

**Pattern B — Board-level family grouping.** `miatoll` (5 entries) and `Mi439` (7 entries)
cover devices that share a common kernel/board tree but have distinct hardware identities.
These are closer to "family" grouping but still use exact strings — the config is simply
written to serve the whole board family.

**Pattern C — Marketing name alongside codename.** OnePlus configs include both the Android
codename and the marketing model name string (e.g., `enchilada` + `OnePlus6`). This is
because some OnePlus devices report the marketing name rather than the codename over USB.

**Pattern D — Single-entry configs.** Fairphone, most Pixels, single-variant Samsungs, and
single-variant Xiaomis carry exactly one code. These are truly variant-specific.

**Conclusion for the verifier:** The matching strategy is: read the exact device code the device
reports, look it up in `supported_device_codes`. No fuzzy matching, no family matching, no
prefix stripping. A device that reports `hero2ltexx` will match the `hero2lte` config because
`hero2ltexx` is explicitly listed. A device reporting `hero2ltekr` (not listed) would find no
config. **The verifier can use the same exact-match strategy without losing precision the OAI
configs were designed with.**

---

## Q2 — Structural consistency: unlock_bootloader and is_ab_device

**Conclusion: `is_ab_device` is declared 100% — enforced by schema. `unlock_bootloader` is
declared in all configs but may be `null` (empty step list), which is structural and intentional.**

### `is_ab_device`

The schema in `installer_config.py` requires `is_ab_device` as a non-optional boolean field
in every config's `metadata` block. There are no exceptions. The schema validation rejects any
config file that omits it. Every one of the 43 configs examined declared it.

Distribution across the 43 examined:

- `is_ab_device: false` — Samsung (all examined: herolte, hero2lte, a-series, S4, S5, S6,
  S8, S9, Note 8, Note 9, A72), Xiaomi/POCO (alioth, miatoll, Mi439, lavender, ginkgo,
  surya, vayu, raphael, cupid), Fairphone 2, OnePlus One (bacon), OnePlus 3/3T (oneplus3)
- `is_ab_device: true` — Fairphone 3, Fairphone 4, Sony Xperia 10 (kirin), OnePlus Nord
  (avicii), OnePlus 6/7/7T variants, Google Pixel 2/3/3a/4/4a/4XL/5/5a and XL variants

### `unlock_bootloader` step presence

The schema declares `unlock_bootloader` as `schema.Or(None, [step_schema])` — it is required
to be present as a key but is allowed to be `null` (Python `None`). The code in `from_file()`
converts `null` to an empty step list.

**Null `unlock_bootloader` is intentional and meaningful:** it signals that the device's
bootloader unlock is not a procedure the tool can automate. Observed in all Exynos Samsung
configs (herolte, hero2lte, a-series, dreamlte, starlte, crownlte, greatlte, a72q, etc.).
For these devices, the user is assumed to have used the OEM unlock toggle in Android settings,
and the tool skips directly to flashing the recovery via Heimdall.

**Populated `unlock_bootloader` steps:** present in all Qualcomm/standard fastboot devices —
Fairphone 3/4, all OnePlus configs, all Pixel configs, Xiaomi/POCO configs, Sony kirin.

**No config omits the `unlock_bootloader` key entirely.** Every config has the key; it is
either `null` or a list of steps.

### Summary

| Field | Declared in all 93 configs? | Exceptions |
|---|---|---|
| `is_ab_device` | Yes — schema-enforced | None possible |
| `unlock_bootloader` key present | Yes — schema-enforced | None |
| `unlock_bootloader` populated with steps | No — intentionally null for Samsung Exynos | ~25–30 configs have null (all Samsung Exynos-type) |

---

## Q3 — USB mode tracking in configs

**Conclusion: Configs do not declare USB modes as metadata. Mode transitions are implicit
in the step sequence, readable by inspecting the `command` fields in order.**

The configs have no field named `usb_mode`, `mode_transition`, or equivalent. There is no
explicit declaration of what USB mode the device is in at each step. However, the commanded
transitions are fully recoverable by reading the command sequence:

### How mode transitions appear in configs

Each step that issues a `command` drives a mode transition. The mode before and after is
deterministic for each command:

| Command | Mode before | Mode after |
|---|---|---|
| `adb_reboot_bootloader` | ADB (Android running) | Fastboot / bootloader |
| `adb_reboot_download` | ADB (Android running) | Samsung Download Mode (Odin/Heimdall) |
| `fastboot_unlock` | Fastboot | Fastboot (reboots, back to Fastboot or Android) |
| `fastboot_oem_unlock` | Fastboot | Fastboot (reboots, Android) |
| `fastboot_unlock_critical` | Fastboot | Fastboot |
| `fastboot_reboot` | Fastboot | Android |
| `fastboot_boot_recovery` | Fastboot | Recovery (temporary, RAM-boot) |
| `fastboot_flash_recovery` | Fastboot | Fastboot (recovery written to partition) |
| `fastboot_reboot_recovery` | Fastboot | Recovery (permanent flash then reboot) |
| `fastboot_flash_boot` | Fastboot | Fastboot (boot partition written) |
| `fastboot_flash_additional_partitions` | Fastboot | Fastboot |
| `heimdall_flash_recovery` | Samsung Download Mode | Download Mode continues |
| `adb_twrp_copy_partitions` | ADB (in TWRP recovery) | ADB (in TWRP recovery, reboots to bootloader) |
| `adb_sideload` | ADB (in sideload mode in recovery) | ADB (sideload completes) |
| `fastboot_unlock_with_code` | Fastboot | Fastboot (reboots to Android) |

### Typical mode-transition sequences

**Samsung Exynos (herolte, hero2lte, a-series, dreamlte, etc.):**
- unlock_bootloader: null (OEM toggle only, no USB mode change by tool)
- boot_recovery: Android (ADB) → `adb_reboot_download` → Samsung Download Mode →
  `heimdall_flash_recovery` (stays in Download Mode) → manual reboot by user → Recovery

**Standard Fastboot (Google Pixel, OnePlus, Fairphone 3/4, Sony kirin):**
- unlock_bootloader: Android (ADB) → `adb_reboot_bootloader` → Fastboot →
  `fastboot_unlock` or `fastboot_oem_unlock` → [reboot Android] → [ADB again] →
  `adb_reboot_bootloader` → Fastboot
- boot_recovery: Fastboot → `fastboot_boot_recovery` → Recovery

**Xiaomi Mi Unlock (lavender, surya, vayu, raphael, alioth, miatoll, etc.):**
- unlock_bootloader: Mi Unlock app (Windows, no ADB step by the tool) — link_button_with_confirm only, user handles USB
- boot_recovery: Android (ADB) → `adb_reboot_bootloader` → Fastboot →
  `fastboot_flash_recovery` → `fastboot_reboot_recovery` → Recovery

**Sony Xperia (kirin) — code+IMEI unlock:**
- unlock_bootloader: Android (ADB) → `adb_reboot_bootloader` → Fastboot →
  `fastboot_unlock_with_code` (user enters 18-char code) → [reboot Android]
- boot_recovery: Android (ADB) → `adb_reboot_bootloader` → Fastboot →
  `fastboot_flash_boot` → Recovery → `adb_twrp_copy_partitions` → Fastboot →
  `fastboot_flash_boot` → Recovery

**Re-enumerations per method:**

| Config type | USB mode changes during full install |
|---|---|
| Samsung Exynos (null unlock) | 2 (Android → Download Mode → Recovery, after manual reboot) |
| Standard Fastboot (Pixel, OnePlus) | 4–5 (Android → Fastboot → Android → Fastboot → Recovery → possibly more) |
| Xiaomi (Mi Unlock) | 3 (Mi Unlock app phase invisible to OAI; then Android → Fastboot → Recovery) |
| Sony kirin | 5+ (Android → Fastboot → Android → Fastboot → Recovery → ADB → Fastboot → Recovery) |
| AB devices with copy_partitions | +1 additional (recovery → bootloader re-entry) |

**Key finding:** The USB mode during the Mi Unlock step (Xiaomi devices) is not tracked at all
by the config. The user runs the Mi Unlock Windows app independently; the OAI tool has no ADB
or fastboot contact with the device during that phase. The config uses `link_button_with_confirm`
— a UI step with no `command` — so no mode transition is recorded.

---

## Q4 — Browser/WebUSB terminology

**Conclusion: No WebUSB vocabulary exists anywhere in OAI configs or documentation.
The tool is a native desktop app; "browser" is not a concept in its architecture.**

**Code search result:** A full-text search of the OAI repository for "webusb", "browser",
"enumerate", "invisible", "not detected", "cannot see" returned zero matches in configs
or documentation files.

**Architecture explanation:** OpenAndroidInstaller is a native Python desktop application
(using the Flet/Flutter framework). It communicates with devices via `adb`, `fastboot`, and
`heimdall` command-line binaries bundled with the distribution. These are native OS-level USB
drivers, not WebUSB. The application has no web frontend and is not a browser extension.

**Issue tracker:** A search of open issues for USB detection problems found only classic
ADB/fastboot "device not found" error reports — the kind caused by missing udev rules on
Linux or missing USB drivers on Windows. Issue #620 is a representative example: the device
was visible to `fastboot devices` on the terminal but OAI failed to find it, due to a
bundled-binary path issue, not a USB enumeration visibility problem.

**Terminology OAI uses for failure to detect a device:**
- "Failed to detect a device" — the UI message in `start_view.py` (`search_devices_clicked`)
- "Failed to detect a device" — the log message in `tooling.py` (`search_device`)
- No vocabulary for the distinction between "OS can see device" and "app cannot see it"

**Implication for Flashguard:** OAI has no existing vocabulary for the WebUSB visibility
problem Flashguard is studying. If Flashguard introduces terminology for
"device OS sees it, browser WebUSB cannot enumerate it", that vocabulary is genuinely new
and not borrowed from OAI.

---

## Q5 — Asset integrity tracking

**Conclusion: OAI configs store no checksums. No ROM hash, no recovery hash.
ROM and recovery files are user-provided; the tool does not verify their integrity.**

Evidence from the schema (`installer_config.py`):

The `metadata` block schema allows: `maintainer`, `device_name`, `is_ab_device`, `device_code`,
`supported_device_codes`, `untested`, `twrp-link`, `additional_steps`, `notes`, `brand`.
No checksum or hash field is present or schema-validated.

The `requirements` block allows only `android` (version string) and `firmware` (version
string). No hash.

None of the 43 configs examined contain any field resembling a checksum or file hash.
The `notes` field in some configs (alioth, ginkgo, Mi439) contains human-readable advice
about which ROM version to choose, but these are user guidance strings, not machine-verifiable
hashes.

**Where ROM/recovery files come from:** The user is directed to download them themselves (usually
from the LineageOS website or a recovery project page). OAI does not verify what they downloaded.

**What a safety verifier can check from OAI configs:** Nothing related to asset integrity.
The configs contain zero hash data. If Flashguard needs to verify that a ROM file matches
a known-good checksum, that information must come from a separate source (e.g., the LineageOS
build manifest, which does include SHA-256 hashes for official builds).

---

## Q6 — Prerequisite field patterns

**Conclusion: OAI tracks two formal prerequisite fields: `requirements.android` and
`requirements.firmware`. No bootloader version, kernel version, partition scheme, or
verified boot state prerequisites exist as structured fields.**

### Formal prerequisite fields (schema-enforced)

| Field | Type | What it means | Example values |
|---|---|---|---|
| `requirements.android` | string or int | Minimum Android version the device must be running before starting | `12`, `"12.1.0"`, `"10 (Q)"`, `11`, `"12 (S)"` |
| `requirements.firmware` | string | Specific firmware/MIUI version required | `"MiUI 12.5 (Q)"` |

Both are optional (the `requirements` block itself may be absent). When absent, the tool
imposes no prerequisite check.

### Informal prerequisites (in step content text, not machine-readable)

Several configs include human-readable prerequisite information in step `content` strings that
the tool displays but does not automatically verify:

- **Xiaomi configs:** The Mi Unlock step text explains the 30-day waiting period, SIM requirement,
  and Mi account requirement. These are prerequisites but the tool cannot check them.
- **Sony kirin:** The step text requires checking the "Bootloader unlock allowed: Yes" status
  in the service menu. The tool cannot read this; it asks the user to confirm.
- **alioth notes field:** Contains guidance about OrangeFox recovery version codes. Machine-
  readable field but contains free text advice, not a structured constraint.
- **OnePlus AB configs (avicii, enchilada, etc.):** The `adb_twrp_copy_partitions` step
  addresses the inactive A/B slot firmware skew problem. This is a prerequisite check
  (is the inactive slot populated?) that the tool handles by just running the copy unconditionally.

### What "prerequisites_met" should check against OAI configs

Based on what the configs formally declare:

1. **Android version** — `requirements.android` is present in about half the examined configs.
   The verifier can read this and compare against the reported Android version from the device.
   Caveat: the format is inconsistent (`12`, `"12.1.0"`, `"10 (Q)"`) — requires normalisation.
2. **Firmware version** — `requirements.firmware` appears only in Mi439 in the examined set.
   Matches against MIUI version; not readable without a `getprop` call.
3. **Bootloader OEM unlock toggle** — Not a formal field, but Samsung Exynos configs (null
   unlock step) implicitly require this to have been enabled beforehand. No machine-readable
   signal.
4. **Vendor account and waiting period** — Not in any config field. Human-only.

**Gap summary:** The only machine-readable prerequisite OAI exposes is the Android version
requirement. Everything else is human-readable text in step content, or entirely absent.

---

## Q7 — Device fingerprinting readiness

**Conclusion: OAI configs cannot be matched to a real device fingerprint from USB descriptors.
The only match key is the device code string, which the tool reads via ADB (`adb_get_state`
equivalent). USB-descriptor-level matching is not possible from OAI data alone.**

### What metadata is available per config

| Metadata field | Present? | Usable for fingerprinting? |
|---|---|---|
| `device_code` | Yes, every config | Yes — primary match key, but only after ADB is running |
| `supported_device_codes` | Yes, every config | Yes — same, exact-string match |
| `device_name` | Yes — human-readable string | No — free text, not normalised |
| `is_ab_device` | Yes, every config | Partial — helps verify after matching, not for initial match |
| `brand` | Optional, ~30% of examined configs (Xiaomi/POCO) | No — free text |
| `maintainer` | Yes | No — not a device property |
| `requirements.android` | ~50% of examined configs | Partial — useful as a post-match sanity check |
| `requirements.firmware` | Rare (~1–2 configs) | No — MIUI-specific |
| `twrp-link` | ~10% | No — a web URL fragment |

**No config contains:**
- USB Vendor ID or Product ID
- Partition scheme (A-only / A/B / VAB is captured in `is_ab_device` as a boolean, not as
  a scheme descriptor)
- Bootloader version or chip identifier
- Radio hardware variant information
- `ro.build.fingerprint` or any Android property beyond the device code

**How OAI actually matches a device to a config:** It calls `adb get-serialno` or equivalent
on-device shell commands to retrieve the device code string, then searches configs for it.
The matching occurs at the ADB layer, not the USB descriptor layer. A device in fastboot mode
is matched via `fastboot getvar product`.

**Implication for Flashguard:** If Flashguard reads USB descriptors (VID/PID from `lsusb`)
rather than ADB properties, OAI configs cannot be directly matched. The verifier would need
to either:
- Also read ADB properties (which changes it from a pure USB-descriptor verifier), or
- Build a separate VID/PID → device_code mapping table

Neither is in the OAI config format.

---

## Q8 — Config maintenance status

**Conclusion: Active maintenance. Most recent config-touching commit: 2025-03-29.
All 30 commits retrieved touch the configs directory; the oldest in the retrieved set
is from 2023-12-27. No abandoned configs were visible from commit dates alone.**

### What the commit history shows

The 30 most recent commits touching `openandroidinstaller/assets/configs/` span:
- **Most recent:** 2025-03-29 (image transparency fix across all configs)
- **Oldest in the 30-commit window:** 2023-12-27 (addison config added)

Primary maintainers active on configs:
- **SirRGB** — the most active contributor, adding and fixing device configs
- **tsterbak (Tobias Sterbak)** — project maintainer, both code and configs

Commit messages show a pattern of: config addition (referencing LineageOS BoardConfig.mk for
device asserts), config corrections (fixing issue reports), and marking configs as tested.

**Observable pattern:** New configs are often copied from existing similar configs and then
marked `untested: true`. Once a user reports success, the `untested` flag is removed. Example:
commit `05f08c0` is titled "configs: mark ali as tested" — a follow-up to the initial add.

**Cannot determine from API alone:** Which individual files have not been touched in 2+ years.
Doing that requires per-file `git log` queries across all 93 files. The 30-commit window
retrieved covers activity across the whole config directory, not per-file dates.

**Staleness risk:** The `removed/` directory contains 3 configs (`beyond0lte.yaml`,
`beyond1lte.yaml`, `beyond2lte.yaml` — Samsung Galaxy S10 variants). These were removed from
active use, indicating the project does prune configs that no longer work. The existence of a
`removed/` directory is a positive signal for corpus hygiene.

---

## Q9 — Test coverage and known working

**Conclusion: OAI uses a binary tested/untested flag (`untested: true`) in the config
metadata. Absence of the flag means tested (or at least: claimed to work). There is no
device matrix, no test log, no formal test record.**

### The `untested` field

The schema in `installer_config.py` declares:
```
schema.Optional("untested"): bool
```

Presence in configs examined:

| Config | `untested: true`? |
|---|---|
| a7y17lte | Yes |
| alioth | Yes |
| surya | Yes |
| miatoll | Yes |
| cupid | Yes |
| jfltexx | Yes |
| ginkgo | Yes |
| raphael | Yes |
| oneplus3 | Yes |
| All Pixel configs examined | No |
| All Fairphone configs | No |
| herolte, hero2lte, a5xelte, a5y17lte, a3y17lte, a7xelte | No |
| dreamlte, starlte, crownlte, greatlte | No |
| avicii, enchilada, guacamole, guacamoleb, hotdog, hotdogb | No |
| kirin, lavender, vayu, klte, zeroltexx, zerofltexx | No |
| bacon | No |

Roughly 9 of 43 examined (21%) carry `untested: true`. The commit history confirms the flag
is actively managed — commits like "mark ali as tested" show the project removes the flag when
verification is reported.

**No device matrix:** There is no CSV, JSON, or structured file recording which devices have
been tested, by whom, on what date, with which ROM version. The only record is the presence or
absence of `untested: true` in the per-device YAML and the commit history where the flag changed.

**No test reports:** No `tests/` directory for device configs. The project's test suite covers
Python unit tests for the application code, not device-level verification.

**Implication for Flashguard:** `untested: true` maps directly to `cannot-verify`. A config
marked `untested` has not been verified by any human who reported back to the project.
The absence of `untested` is a weak trust signal — it means someone tried it and it worked,
but there is no timestamp, no version pin, and no formal record. It is community testimony,
not a test log.

---

## Q10 — Config quality tiers

**Conclusion: OAI has a single binary quality dimension: `untested` flag yes/no.
There is no multi-tier classification (official / community / experimental / deprecated).
The only additional signal is the `maintainer` field, which records who authored the config.**

### Quality signals available

| Signal | What it indicates | Machine-readable? |
|---|---|---|
| `untested: true` absent | Someone reported it working | Yes |
| `untested: true` present | Authored but unverified | Yes |
| `maintainer` = "Tobias Sterbak (tsterbak)" | Project maintainer authored it directly | Yes (string match) |
| `maintainer` = "A non (anon)" | Community-contributed, low provenance | Yes (string match) |
| Config in `removed/` directory | Removed from active corpus | Inferrable from path |
| `requirements.android` present | Author thought firmware level mattered enough to document | Yes |
| `notes` field present | Something non-standard about this device | Yes |

**No promotion/demotion criteria are documented.** There is no CONTRIBUTING policy that defines
what must be true before removing `untested`. The pattern inferred from commits is: a user
reports success in an issue, a maintainer removes the flag. That is the entire lifecycle.

**Trust signal an automated verifier can inherit:**
- `untested: true` → `cannot-verify` verdict is defensible
- `untested` absent + maintainer is tsterbak → strongest trust signal available
- `untested` absent + maintainer is "A non (anon)" + has `requirements` → medium trust
- Config in `removed/` → do not use, `cannot-verify`

---

## Q11 — Variant-agnostic pattern examples

**Yes. The two-tier structure already exists, implicitly.**

OAI's approach: one config file covers a device family via `supported_device_codes`, which
lists all known variant codes explicitly. The config body (unlock procedure, recovery flash
procedure) is written for the common case and assumes all listed variants can follow the same
steps.

### Strongest multi-variant examples

**`Mi439.yaml`** (7 device codes, 4 distinct product names):
Covers Xiaomi Redmi 7A (`pine`), Redmi 8 (`olive`), Redmi 8A (`olivelite`), Redmi 8A Dual
(`olivewood`, `olives`), plus capitalisation variants of Mi439. All share the same Qualcomm
Snapdragon 439 board and the same Mi Unlock → Fastboot → TWRP procedure. The config works
because the shared board means the procedure is identical.

**`miatoll.yaml`** (5 device codes, multiple product names):
Covers Redmi Note 9S (`miatoll`), Redmi Note 9 Pro (`curtana`), Redmi Note 9 Pro Max
(`excalibur`), Redmi Note 10 Lite (`joyeuse`), Poco M2 Pro (`gram`). All are Snapdragon 720G
board variants. Single config, same procedure.

**`oneplus3.yaml`** (4 codes — OnePlus 3 AND OnePlus 3T):
Notably covers two different products (3 and 3T) in one config. They share a board and the
same fastboot_oem_unlock procedure. This is an explicit design choice — the commit message
references both devices.

**`klte.yaml`** (8 codes — Samsung Galaxy S5 carrier variants):
All US carrier and international variants of the same phone. Procedure is identical across
all.

### Variant differences that DO cause separate configs

The Samsung Exynos/Qualcomm split is the clearest example. `jfltexx` (S4 Qualcomm) uses
Heimdall in Download Mode. A hypothetical S4 Exynos config would as well, but the procedure
may differ. OAI keeps these separate.

The `guacamole` (OnePlus 7 Pro) and `guacamoleb` (OnePlus 7) are separate files despite
being closely related — they differ in hardware (display, cameras) but not in the install
procedure. Both list only their own code.

**Two-tier matching strategy in OAI terms:**
- Tier 1: exact code → find the config file
- Tier 2: follow the single procedure for that file regardless of which variant code matched

There is no logic in OAI that adapts the procedure based on which variant code was matched.
The procedure is identical for all codes in a config.

---

## Q12 — Cross-project alignment with LineageOS

**Conclusion: OAI configs are derived from LineageOS device configs, but are not kept
in sync automatically. Alignment is manual and commit-message-based.**

### Evidence

Commit messages in the recent history explicitly cite LineageOS device repositories:

- `"asserts taken from https://github.com/LineageOS/android_device_motorola_montana/blob/.../BoardConfig.mk#L17"` (addison, montana configs)
- `"asserts taken from https://github.com/crdroidandroid/android_device_motorola_potter/blob/.../BoardConfig.mk#L61"` (potter)
- `"asserts taken from https://github.com/LineageOS/android_device_oneplus_billie/blob/.../BoardConfig.mk#L86"` (billie)

This means **OAI contributors manually pull the device assertions (which determine which
device code strings to list in `supported_device_codes`) from LineageOS BoardConfig.mk
files**. This is the cross-project reference mechanism.

**Not kept in sync automatically:** There is no CI job that regularly updates configs from
LineageOS. New LineageOS devices are added to OAI by human contributors who notice a gap and
open a PR with the new config.

**Divergence risk:** LineageOS may add new variants of an existing device (new regional codes)
without OAI being updated. The `a7y17lte` config only has 2 codes while the LineageOS wiki
may cover more.

**For the verifier:** Cross-project alignment means OAI's device code lists are derived from
LineageOS's hardware database. A device that LineageOS officially supports is more likely to
have a correct, working OAI config (because the device tree was the reference). Devices that
are only community-ported may have OAI configs that are inaccurate.

---

## Q13 — Error handling and fallback

**Conclusion: No "try a similar device" fallback. If no config matches, the user is told
there is no config and shown a list of supported devices.**

### What happens when no config is found

From `installer_config.py`:

```python
logger.info(f"No device config found for device code '{device_code}'.")
return None
```

The function returns `None`. The calling code in the start view then handles this by
displaying a "device not supported" message and listing supported devices. There is no
fuzzy fallback, no family suggestion, no "did you mean X?" logic.

### No config adaptation at runtime

The tool does not detect which variant code matched and adapt the procedure. All variants
in a config receive exactly the same steps. If a new variant code appears that is not in any
config's `supported_device_codes`, it gets no config at all.

**User experience when unsupported:** The project directs users to submit a GitHub issue or
contribution. There is no in-app guidance for trying a similar device's config.

---

## Q14 — Schema stability indicators

**Conclusion: The schema is stable and well-bounded. No deprecated fields were observed.
Recent additions (`brand`, `notes`, `additional_steps` types) are backward-compatible
optional fields.**

### Schema as defined in `installer_config.py` (complete metadata fields)

Required fields:
- `maintainer: str`
- `device_name: str`
- `is_ab_device: bool`
- `device_code: str`
- `supported_device_codes: [str]`

Optional fields:
- `untested: bool`
- `twrp-link: str`
- `additional_steps: [regex: dtbo|vbmeta|vendor_boot|super_empty]`
- `notes: [str]`
- `brand: str`

Requirements block (entirely optional):
- `requirements.android: str or int`
- `requirements.firmware: str`

Step schema (required fields per step):
- `type: regex(text|confirm_button|call_button|call_button_with_input|link_button_with_confirm)`
- `content: str`

Step schema (optional fields per step):
- `command: regex(enumerated list of allowed commands)`
- `allow_skip: bool`
- `img: str`
- `link: str`

### Command whitelist (full enumeration from schema)

All commands that configs are permitted to use:
`adb_reboot`, `adb_reboot_bootloader`, `adb_reboot_download`, `adb_sideload`,
`adb_twrp_wipe_and_install`, `adb_twrp_copy_partitions`, `fastboot_boot_recovery`,
`fastboot_flash_boot`, `fastboot_flash_recovery`, `fastboot_unlock_critical`,
`fastboot_unlock_with_code`, `fastboot_get_unlock_data`, `fastboot_unlock`,
`fastboot_oem_unlock`, `fastboot_reboot`, `fastboot_reboot_recovery`,
`heimdall_flash_recovery`, `fastboot_flash_additional_partitions`

This is a strict whitelist — configs cannot invoke arbitrary commands.

### Stability assessment

- **No deprecated fields observed.** None of the 43 configs uses a field that the current
  schema rejects.
- **`vendor_boot` in `additional_steps`** was added at some point to support newer A/B
  devices requiring vendor_boot partition flashing. This is a recent addition.
- **`brand` and `notes`** appear to be additions made as the config set grew (Xiaomi family
  configs use `brand: xiaomi`/`poco`).
- **The command whitelist** is the most stable element — it has been carefully bounded and
  each command corresponds to a specific function in `tooling.py`.

**The schema is stable enough for the verifier to rely on.** Fields will not disappear.
New optional fields may be added, but the required structure is frozen by the validation layer.

---

## Summary of all 14 questions

| Question | Answer |
|---|---|
| Q1: supported_device_codes — exact or family? | **Exact strings only. Zero wildcards.** Multiple variants listed explicitly per codename suffix. |
| Q2: 100% have unlock_bootloader + is_ab_device? | **`is_ab_device`: 100%, schema-enforced. `unlock_bootloader`: key always present, but `null` for Samsung Exynos (~25–30 configs).** |
| Q3: USB mode tracking in configs? | **No explicit USB mode fields. Mode transitions are implicit in the command sequence and fully recoverable.** |
| Q4: Browser/WebUSB terminology? | **Zero. OAI is a native app. No WebUSB concepts exist. The vocabulary gap is real and new.** |
| Q5: Asset integrity — checksums? | **None. Zero hash fields in any config or schema. ROM integrity is entirely the user's problem.** |
| Q6: Prerequisite field patterns? | **Two formal fields: `requirements.android` and `requirements.firmware`. Everything else is human-readable step text.** |
| Q7: Fingerprinting readiness? | **Cannot match from USB descriptors. Matching requires ADB/fastboot device code read. No VID/PID data.** |
| Q8: Config maintenance status? | **Active. Oldest configs visible in 30-commit window: 2023. `removed/` directory confirms pruning. Two primary maintainers.** |
| Q9: Test coverage? | **Binary `untested` flag only. No device matrix. ~21% of examined configs are `untested: true`.** |
| Q10: Config quality tiers? | **Two tiers: tested (flag absent) and untested (flag present). No further classification.** |
| Q11: Variant-agnostic configs? | **Yes — `Mi439` (7 codes), `miatoll` (5 codes), `oneplus3` (3+3T), `klte` (8 carrier variants). All use exact-string lists.** |
| Q12: Cross-project LineageOS alignment? | **Manual derivation. Contributors cite LineageOS BoardConfig.mk as the source for device asserts. No automated sync.** |
| Q13: Error handling / fallback? | **None. No match → `None` returned → "device not supported" message. No fuzzy fallback.** |
| Q14: Schema stability? | **Stable. Required fields frozen. Optional fields (brand, notes) backward-compatible. Command whitelist is a bounded set of 18 commands.** |

---

## What this means for Flashguard

**Safe to rely on:**
- The exact-string match strategy. The verifier can use `device_code in supported_device_codes`
  without needing fuzzy logic. No OAI config uses patterns.
- `is_ab_device` as a boolean. It is present in all configs and machine-readable.
- The `untested` flag as a `cannot-verify` signal. It is schema-validated and actively managed.
- The command whitelist. The 18 allowed commands are the exhaustive set of USB-mode transitions
  OAI configs can order. Any new config must use one of these.

**Cannot rely on:**
- USB-descriptor-level matching. OAI configs have no VID/PID data.
- ROM checksums. There are none.
- Bootloader version prerequisites. There are none.
- Partition scheme declarations beyond `is_ab_device` (true/false).
- Any WebUSB vocabulary. It does not exist.
- Automatic cross-project sync with LineageOS. Alignment is manual and may lag.

**Directly usable by Flashguard:**
- `requirements.android` for a minimum Android-version prerequisite check (after normalisation
  of the inconsistent format strings).
- The `untested` field for a `cannot-verify` override regardless of other signals.
- `supported_device_codes` as the primary recipe-to-device matching table.
- The command sequence as an implicit USB-mode transition graph for understanding what a given
  recipe requires of the USB connection at each step.

*Research conducted 2026-09-15. Sources: GitHub API, openandroidinstaller-dev/openandroidinstaller, main branch. No config YAML text reproduced verbatim.*

---

# Analysis, 15 September, by the analysing session

Good research, and the Q1 answer is solid on the mechanism. Checking it against our own code
turned up something larger than the question it was sent to settle.

## 1. The variant check has never been able to pass, on any device, ever

`flashguard/verify.py` reads `fingerprint.get("variant")` and abstains when it is absent. **No
fingerprint has that field.** Verified by running the real corpus replay against the real
Samsung A5 capture:

```
fingerprint keys: android_version, board_platform, bootloader_basis, bootloader_state,
  bootloader_unlockable, build_fingerprint, chipset_family, chipset_source, cpu_abi,
  hardware, manufacturer, partition_basis, partition_scheme, product_device,
  product_model, sdk, security_patch, slot_suffix, verified_boot_state
  variant        = None
  product_device = 'a5xelte'
```

Nineteen fields, and `variant` is not among them. `data/schema.md` does not define it either;
it defines `variant_confirmed_by` but never the thing being confirmed. So `missing-variant`
fires unconditionally, on every record, forever.

**A check that can never pass is not conservatism. It is a stuck switch.** It has been reading
as caution on every run since 13 September, and part of `decided 0/5` is this, not the matrix
gap it has been attributed to.

This is the same class as the corpus replay checking each recipe against itself and the
privacy check reading the wrong line: a mechanism reporting something defensible for a reason
nobody had looked at.

## 2. Which means the DISPUTED question was aimed at the wrong thing

The marker asks whether `supported_device_codes` is a variant-level or a family-level claim.
But look at what the recipes actually hold:

Checked on all five rather than a sample:

| recipe | `target.product_device` | `target.variant` |
|---|---|---|
| a5xelte-recovery-independent-facts.json | `a5xelte` | `a5xelte` |
| avicii-multi-image-facts.json | `avicii` | `avicii` |
| fp3-unlock-independent-facts.json | `FP3` | `FP3` |
| fp4-independent-facts.json | `FP4` | `FP4` |
| kirin-unlock-independent-facts.json | `kirin` | `kirin` |

Five for five, identical strings.

**`target.variant` is the OAI device codename.** It is the same string, from the same source, as
`product_device`. The recipe stores one identifier under two names and the verifier checks it
twice: once as a device code, where it passes, and once as a variant, where it abstains because
that field was never captured.

So the device has already reported its variant. It is called `product_device` in the schema and
`variant` in the recipe.

**The research settles the mechanism question anyway, and in position A's favour.** Membership
in `supported_device_codes` is a plain `in` test against exact strings that a human deliberately
enumerated. `hero2lte`'s config explicitly lists `hero2ltexx`. Position B worried that a shared
base code says nothing about the variant, and it is right that a *prefix inference* would say
nothing. This is not a prefix inference. It is a curated list.

**One caveat the research supplies against its own headline.** Two configs group genuinely
distinct hardware: `miatoll` covers five board variants and `Mi439` covers seven devices the
research itself describes as "distinct hardware". Each still reports its own code, so they stay
distinguishable, but a recipe's prerequisites may have been established against one member and
not another. That is a reason for care on the prerequisite axis, not the identity axis.

**And the identity axis does not have to carry the burden**, because `safe` already requires a
fingerprint confirming the required state, read from the device. Relaxing identity does not open
a false-safe path while the state checks stand.

**Three options, and this is Ranaji's call, not the producer's:**

- **(a)** Drop `variant` from the recipe format. It duplicates `product_device` and nothing can
  populate it. Same shape as the `state` decision.
- **(b)** Keep it and define it as something `product_device` is not, such as a hardware
  revision within one device code, then add it to the schema and capture it. Real work, and
  nothing in the evidence so far says it is needed.
- **(c)** Leave it and keep abstaining. Honest only if the abstention is understood as "we do
  not capture this", which is not what the reason text currently says.

Whatever is chosen, the `missing-variant` reason text must stop implying the device failed to
report something. It did report it.

## 3. The most actionable finding in the whole document is Q9

OAI carries a machine-readable `untested: true` flag, schema-declared and optional, meaning the
config was authored but never confirmed on hardware. **None of our five recipes carries it**,
and their `source` blocks record `device_facts_from`, `consulted` and `authored` but not this.

**A recipe derived from an untested upstream config must never reach `safe`.** That is a cheap,
high-value rule that comes from upstream's own data rather than from our judgement, and it is
exactly the kind of provenance the verdict contract already reasons about. Carry the flag into
the recipe `source` block and let it gate the verdict.

## 4. Two findings that settle open questions elsewhere

**`is_ab_device` is schema-enforced and non-optional.** The survey's 90 of 90 was not a happy
accident, it is a validation rule, so it can be relied on as an invariant for this corpus. That
answers the second question sent to OAI without needing a reply.

**Zero WebUSB vocabulary anywhere in OAI, confirmed by full-text search**, and the architectural
reason is given: it is a native desktop application driving `adb`, `fastboot` and `heimdall`. So
two of the three projects asked have now said the concept does not exist in their world. That is
not a gap in our search; it is the concept being new to the browser route, and the proposal
should say so plainly.

## 5. One gap worth naming as a deliberate non-goal

**OAI stores no checksums.** No ROM hash, no recovery hash, nothing schema-validated. The ROM
and recovery files are user-provided and their integrity is never checked. That is a real
ecosystem gap and it is adjacent to ours without being ours: Flashguard verifies a device
against a recipe, not an artefact against a hash. Say so explicitly in the proposal rather than
leaving a reviewer to wonder whether it was missed.
