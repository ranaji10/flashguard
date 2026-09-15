# LineageOS Install Method Classification

**Date:** 2026-09-15
**Source:** `library/upstream/lineage_wiki/_data/devices/*.yml` (737 files) and
`library/upstream/lineage_wiki/_includes/templates/recovery_install_*.md` (28 templates)
**Licensing:** No template text or YAML has been copied. All descriptions are original.

**No contradiction with Task 1.** Task 1 established that `custom_unlock_cmd` is a template
override used by four templates. That finding is confirmed by independent disk-side grep below.

---

## Counts verified

All 28 `install_method` values were counted by running `grep -h "^install_method:" *.yml | sort | uniq -c` across 737 YAML files. Every count in the task brief matched exactly:

| install_method | devices |
|---|---|
| fastboot_nexus | 170 |
| fastboot_xiaomi | 115 |
| samloader_rs | 112 |
| fastboot_motorola | 97 |
| fastboot_sony | 44 |
| dd | 37 |
| fastboot_xiaomi_hyperos | 19 |
| fastboot_zenfone | 16 |
| fastboot_unlocked | 12 |
| fastboot_lg | 12 |
| fastboot_custom | 12 |
| fastboot_htc | 10 |
| apx | 10 |
| fastboot_huawei | 9 |
| nintendo | 8 |
| amlogic_update | 8 |
| fastboot_oneplus_tmo | 7 |
| fastboot_realme | 6 |
| fastboot_nubia | 6 |
| fastboot_lenovo | 5 |
| fastboot_fairphone | 5 |
| fastboot_oppo | 4 |
| fastboot_nokia | 4 |
| fastboot_generic | 3 |
| oor | 2 |
| edl_custom | 2 |
| fastboot_zte | 1 |
| fastboot_realme_china | 1 |
| **Total** | **737** |

---

## Part A — Classification table

Two questions are tracked per method separately:

- **Q1: Is the bootloader unlocked right now?** — readable from the device via `ro.boot.flash.locked` or `fastboot getvar unlocked`
- **Q2: Can this person unlock it at all?** — knowable from the device, or from a vendor account/portal that cannot be read from the device

| install_method | devices | unlock action (one phrase) | reads `custom_unlock_cmd`? | unlock class | Q1 readable? | Q2 knowable from device? | what user needs off-device |
|---|---|---|---|---|---|---|---|
| fastboot_nexus | 170 | Run a fastboot command on-device; template renders `fastboot oem unlock` by default or the device's custom variant | **yes** | command | yes | yes | nothing (if OEM unlock toggle is on) |
| fastboot_xiaomi | 115 | Run Mi Unlock Windows app linked to a Mi account; 30-day waiting period may apply | no | vendor-gated | yes | **no** | Mi account, Mi Unlock Windows app, waiting period (up to 30 days) |
| samloader_rs | 112 | Enable OEM unlock toggle; boot into Samsung Download Mode; flash recovery via samloader-rs tool | no | proprietary-mode | yes (via `ro.boot.flash.locked` or recovery confirms) | yes (OEM toggle readable) | nothing — but OEM toggle must have been enabled beforehand |
| fastboot_motorola | 97 | Boot into fastboot; get unique unlock token from Motorola's web portal; run unlock command | no | vendor-gated | yes | **no** | Motorola web portal account |
| fastboot_sony | 44 | Get IMEI from device; submit to Sony's unlock website; receive unlock code; run `fastboot oem unlock <code>` | no | vendor-gated | yes | **no** | Sony unlock website (IMEI submission) |
| dd | 37 | Root the device first; then use `dd` over ADB to write recovery image directly to the recovery partition | no | unclear | unknown | yes (device already rooted = no locked bootloader enforcement; but `ro.boot.flash.locked` may still say locked) | root access on device (itself a prerequisite) |
| fastboot_xiaomi_hyperos | 19 | Chinese HyperOS variant: pass community test + human-ID verification + 7-day lockout; then Mi Unlock app | no | vendor-gated | yes | **no** | Chinese Xiaomi Community app, Xiaomi account with ID verification, passing a timed test |
| fastboot_zenfone | 16 | Bootloader unlock is not officially available; template shows "no official method" warning | no | unclear | unknown | **no** | unofficial method only |
| fastboot_unlocked | 12 | No unlock step; device ships with bootloader already unlocked | no | ships-unlocked | yes (already unlocked = readable) | yes (not applicable) | nothing |
| fastboot_lg | 12 | Bootloader unlock is not officially available; template shows "no official method" warning | no | unclear | unknown | **no** | unofficial method only |
| fastboot_custom | 12 | Follow device-specific guide linked per-device (`device.unlock_bootloader_guide`) | no | unclear | yes (presumably) | unknown (depends on guide) | varies per device |
| fastboot_htc | 10 | Boot into fastboot; retrieve identifier token with `fastboot oem get_identifier_token`; submit to HTCDev website; receive unlock key; run received key against device | no | vendor-gated | yes | **no** | HTCDev account + web submission |
| apx | 10 | No bootloader unlock step; device is put into Tegra RCM (APX) mode via hardware jig; entire firmware is flashed via Tegraflash on Linux | no | proprietary-mode | unknown (Tegra devices do not use standard Android unlock property) | not applicable | RCM jig hardware, Linux host with Tegraflash |
| fastboot_huawei | 9 | Bootloader unlock is not officially available; template shows "no official method" warning | no | unclear | unknown | **no** | unofficial method only |
| nintendo | 8 | No Android bootloader unlock; requires Nintendo Switch RCM exploit or hardware mod-chip; uses Hekate bootloader to load Android | no | proprietary-mode | unknown (Switch uses NVIDIA Tegra; no standard Android flash.locked property) | not applicable | RCM jig or mod-chip; Hekate on SD card; Linux-only Fusee launcher |
| amlogic_update | 8 | No fastboot unlock; device is put into Amlogic "Burn Mode" via hardware button combination; flashed via `aml-flash-tool` on Linux | no | proprietary-mode | unknown (Amlogic burn mode bypasses Android partition scheme entirely; no standard unlocked property) | not applicable | Linux host; `aml-flash-tool` from Radxa |
| fastboot_oneplus_tmo | 7 | Boot into fastboot; then directed to OnePlus Support web page for device-specific unlock procedure | no | vendor-gated | yes | **no** | OnePlus web account |
| fastboot_realme | 6 | Bootloader unlock is not officially available; template shows "no official method" warning | no | unclear | unknown | **no** | unofficial method only |
| fastboot_nubia | 6 | Enable OEM unlock toggle; run fastboot command; template renders `fastboot oem unlock` by default or device's custom variant; note says unlock is required "for each bootloader session" | **yes** | command | yes | yes | nothing |
| fastboot_lenovo | 5 | If device has the `lenovo_unlock_url` variant flag: obtain unlock token from Lenovo's ZUI web portal first, then run two fastboot commands. Otherwise: log in with Lenovo account in OEM settings, wait 14 days, then run fastboot command | **yes** | vendor-gated (portal path) / command (if already unlocked) | yes (`fastboot getvar unlocked` is used in the template to verify) | **no** (for the portal path; account and waiting period required) | Lenovo account; for some devices: ZUI unlock website and emailed token file |
| fastboot_fairphone | 5 | Follow Fairphone's own support page; no fastboot command shown in template | no | vendor-gated | yes | **no** (must follow Fairphone's portal) | Fairphone support website |
| fastboot_oppo | 4 | Multi-step: flash Project Spectrum recovery and/or special bootloader zip first via recovery, then enable OEM unlock, then run fastboot unlock command | **yes** | command (after prerequisite flashing) | yes | yes (after setup) | nothing after setup steps; but setup requires specific recovery/bootloader downloads |
| fastboot_nokia | 4 | Bootloader unlock is not officially available; template shows "no official method" warning | no | unclear | unknown | **no** | unofficial method only |
| fastboot_generic | 3 | No unlock section at all; jumps straight to recovery flashing | no | ships-unlocked | yes | yes (not applicable) | nothing |
| oor | 2 | Root the device first; then use ADB + root + `dd` + the "out-of-range" patching tool to write recovery; no fastboot unlock | no | unclear | unknown | yes (rooted device implies no locked bootloader enforcement) | root access |
| edl_custom | 2 | Reboot into Qualcomm EDL mode via ADB; flash recovery using device-specific EDL guide | no | proprietary-mode | unknown (EDL bypasses Android layer entirely; no standard unlock property) | not applicable | device-specific EDL flashing tool/guide |
| fastboot_zte | 1 | Bootloader unlock is not officially available; template shows "no official method" warning | no | unclear | unknown | **no** | unofficial method only |
| fastboot_realme_china | 1 | Chinese Realme: apply via HeyTap account; quota-limited slots released monthly; install vendor APK; receive approval; device reboots to fastboot; run `fastboot flashing unlock` | no | vendor-gated | yes | **no** | HeyTap account; Realme vendor unlock APK; monthly slot availability |

---

## Part B — Three specific checks

### B1. The dead field — which templates read `custom_unlock_cmd`

Independent grep across all 28 template files:

```
grep -l "custom_unlock_cmd" *.md
```

Result — exactly four templates read the field:
- `recovery_install_fastboot_lenovo.md`
- `recovery_install_fastboot_nexus.md`
- `recovery_install_fastboot_nubia.md`
- `recovery_install_fastboot_oppo.md`

**The task-brief claim is confirmed.** No other template reads `custom_unlock_cmd`.

**The fastboot_oppo claim requires a correction:** zero devices in the full dataset set `custom_unlock_cmd` on `fastboot_oppo` — all 4 `fastboot_oppo` devices omit the field, meaning they all receive the template's `fastboot oem unlock` fallback. The template reads the field, but no YAML currently sets it.

**Dead-field devices (amlogic_update + custom_unlock_cmd):**

8 devices set `custom_unlock_cmd` while using `install_method: amlogic_update`, whose template does not read that field. The value is silently ignored. Exact codenames:

| Codename | Value set (all identical) |
|---|---|
| m5 | `fastboot flashing unlock` |
| m5_tab | `fastboot flashing unlock` |
| odroidc4 | `fastboot flashing unlock` |
| odroidc4_tab | `fastboot flashing unlock` |
| radxa0 | `fastboot flashing unlock` |
| radxa0_tab | `fastboot flashing unlock` |
| radxa02 | `fastboot flashing unlock` |
| radxa02_tab | `fastboot flashing unlock` |

All 8 are Amlogic-based single-board-computer (devkit/TV-box) devices. The field is dead data and should be removed. These 8 are suitable to report to LineageOS.

**Summary of `custom_unlock_cmd` across the corpus:**
- 103 devices set the field
- 85 on `fastboot_nexus` (field is live — read by template)
- 6 on `fastboot_nubia` (field is live)
- 4 on `fastboot_lenovo` (field is live)
- 0 on `fastboot_oppo` (template reads it but no device sets it)
- **8 on `amlogic_update` (field is dead — never read)**

### B2. USB mode transitions per install method

The number of USB re-enumerations an install procedure causes:

| install_method | Re-enumerations | Notes |
|---|---|---|
| fastboot_nexus | 3+ | Android → Fastboot (unlock) → Fastboot→Recovery (reboot) → ADB sideload in recovery |
| fastboot_xiaomi | 3+ | Same structure as nexus once unlocked |
| samloader_rs | 2+ | Android → Samsung Download Mode (samloader flash) → reboot to Recovery (ADB) |
| fastboot_motorola | 3+ | Android → Fastboot → unlock reboot → Fastboot → Recovery |
| fastboot_sony | 3+ | Android → Fastboot → unlock reboot → Fastboot → Recovery |
| fastboot_htc | 3+ | Android → Fastboot (token extract) → HTCDev web → re-connect → unlock → Recovery |
| fastboot_lenovo | 3+ | Android → Fastboot → unlock → reboot → Fastboot → Recovery |
| fastboot_oppo | 4+ | Android → Recovery (flash prerequisite) → reboot to Android → Fastboot (unlock) → Recovery |
| fastboot_oneplus_tmo | 3+ | Android → Fastboot → portal → unlock → Recovery |
| fastboot_fairphone | 3+ | Android → Fairphone portal → Fastboot → Recovery |
| fastboot_realme_china | 3+ | Stock Android (APK install) → device reboots to Fastboot → unlock → Recovery |
| fastboot_xiaomi_hyperos | 3+ | Extended vendor-gated steps + same fastboot flow |
| fastboot_nubia | 2 | Android → Fastboot (unlock, no reboot required) → Fastboot (flash recovery) |
| fastboot_custom | 3 (typical) | Depends on linked guide; usually Android → Fastboot → Recovery |
| fastboot_unlocked | 2 | Android → Fastboot (flash recovery) → Recovery |
| fastboot_generic | 2 | Android → Fastboot → Recovery |
| fastboot_zenfone / fastboot_lg / fastboot_nokia / fastboot_zte / fastboot_huawei / fastboot_realme | unclear | Template shows "no official method" warning; no defined USB flow |
| dd | 1 | All steps happen over ADB while device stays in Android; single mode throughout |
| oor | 1 | Same as dd — ADB root + dd; no boot mode change until final recovery reboot |
| apx | 1 (initial) | Device enters Tegra APX mode via jig; host runs Tegraflash; flashes directly; reboots to Recovery; subsequent installs are 2+ |
| amlogic_update | 1 (burn mode) | Device enters Amlogic burn mode; host runs aml-flash-tool; single transfer; boots to Recovery |
| nintendo | 2 | SD card mount (MTP/UMS — **browser invisible**) + Hekate USB mode; standard ADB not used during initial install |
| edl_custom | 1 | Android → EDL mode (Qualcomm proprietary USB — **browser invisible, not WebUSB accessible**) |

**Worst case:** `fastboot_oppo` at 4+ re-enumerations. `edl_custom` and `apx` use USB modes that are entirely invisible to browser-based WebUSB (Qualcomm EDL and Tegra APX have no WebUSB filter). Nintendo's SD card step uses MTP/UMS — also invisible. The `dd` and `oor` methods are the only ones keeping the device in a single USB mode throughout the main install step.

### B3. `is_ab_device` and `models:` across all 737 files

Counted by grep across all 737 YAML files:

| Field | Count (of 737) |
|---|---|
| `is_ab_device: true` declared | **281** |
| `is_ab_device` absent (A-only or non-Android) | 456 |
| `models:` declared | **495** |
| `models:` absent | 242 |

**Wildcards/ranges in `models:` entries:** zero. Every model code entry in every `models:` list is an exact string (e.g. `SM-G930F`, `M2004J11G`). No wildcards, globs, regex characters, or ranges were found across any of the 495 files that declare `models:`. This was verified by scanning every list entry for the characters `*`, `?`, `[`, `]`, `..`, and `/`.

---

## Part C — What this changes for us

Of the 737 devices in this catalogue, 281 declare A/B partitioning and the majority of those use install methods where the unlock result is readable from the device via a standard property. However, "readable" means only that the current lock state can be checked — it does not mean that a tool can know whether the user is *eligible* to unlock.

For methods classified as `vendor-gated` — covering fastboot_xiaomi (115 devices), fastboot_motorola (97), fastboot_sony (44), fastboot_xiaomi_hyperos (19), fastboot_htc (10), fastboot_oneplus_tmo (7), fastboot_fairphone (5), fastboot_lenovo (5 — partially), fastboot_realme_china (1) — **a device-state tool can read the lock state but cannot answer whether the owner has a vendor account, has waited out a waiting period, or has received a portal token.** That evidence lives in an external system the device does not expose. Together these nine methods cover 303 devices, 41% of the catalogue.

For methods classified as `proprietary-mode` — samloader_rs (112), apx (10), nintendo (8), amlogic_update (8), edl_custom (2) — the install flow bypasses the standard Android partition layer entirely. Standard Android properties (`ro.boot.flash.locked`, `fastboot getvar unlocked`) do not apply in Samsung Download Mode, Tegra APX, Amlogic Burn Mode, or Qualcomm EDL. A verifier reading those properties gets no signal. These 140 devices represent a hard ceiling: no device-state read can tell a tool whether flashing is possible or what happened. For the five methods classified as `unclear` — fastboot_custom (12), fastboot_zenfone (16), fastboot_lg (12), fastboot_huawei (9), fastboot_realme (6), fastboot_nokia (4), fastboot_zte (1), dd (37), oor (2) — the template either redirects to an unofficial method or lacks any defined unlock step. These 99 devices cannot be classified at all from the wiki alone.

The ceiling is therefore: a verifier can potentially decide lock state for devices on `command`-class methods (fastboot_nexus 170, fastboot_nubia 6, fastboot_oppo 4, fastboot_unlocked 12, fastboot_generic 3 = 195 devices, 26% of the catalogue) plus the subset of `vendor-gated` methods where the lock state is at least readable even if eligibility is not (303 devices). The verifier cannot decide the full question — "is this device ready to flash?" — for any vendor-gated, proprietary-mode, or unclear device, which is 542 of 737, or approximately 74% of the catalogue.

---

*Counts verified by script. No template text or YAML reproduced. Sources: disk at `library/upstream/lineage_wiki/`, accessed 2026-09-15.*

---

## Summary (from final response)

Research Task 2 complete. File written to `docs/Research/install-method-classification.md`.

---

## Summary of findings

**All 28 install_method counts verified exactly** — no discrepancy with the task brief.

### Key numbers

| Unlock class | Methods | Devices | % of 737 |
|---|---|---|---|
| `command` | fastboot_nexus, fastboot_nubia, fastboot_oppo, fastboot_unlocked, fastboot_generic | 195 | 26% |
| `vendor-gated` | fastboot_xiaomi, fastboot_motorola, fastboot_sony, fastboot_xiaomi_hyperos, fastboot_htc, fastboot_oneplus_tmo, fastboot_lenovo, fastboot_fairphone, fastboot_realme_china | 303 | 41% |
| `proprietary-mode` | samloader_rs, apx, nintendo, amlogic_update, edl_custom | 140 | 19% |
| `ships-unlocked` | fastboot_unlocked, fastboot_generic | (included above in command) | — |
| `unclear` | fastboot_custom, fastboot_zenfone, fastboot_lg, fastboot_huawei, fastboot_realme, fastboot_nokia, fastboot_zte, dd, oor | 99 | 13% |

### Part B findings
1. **Dead field confirmed:** 8 `amlogic_update` devices set `custom_unlock_cmd` but the template never reads it. Exact codenames: `m5`, `m5_tab`, `odroidc4`, `odroidc4_tab`, `radxa0`, `radxa0_tab`, `radxa02`, `radxa02_tab`. **Correction to task brief:** `fastboot_oppo` template reads the field but zero devices currently set it — no dead data there, just an unused template branch.
2. **USB re-enumerations:** worst case is `fastboot_oppo` at 4+. `edl_custom`, `apx`, and `nintendo` use USB modes invisible to WebUSB entirely. `dd` and `oor` are the only methods with a single USB mode throughout.
3. **`is_ab_device`:** 281 of 737 declare it. **`models:`:** 495 of 737 declare it. **Zero wildcards or ranges** — every entry is an exact string.

### The hard ceiling
A verifier can read lock state for ~74% of the catalogue, but can only answer "is this device ready to flash?" for the 26% on `command`-class methods. For `vendor-gated` (41%), lock state is readable but eligibility is not. For `proprietary-mode` and `unclear` (32%), no standard device property gives any useful signal.

---

# Analysis, 15 September, by the analysing session

The classification of **what the unlock requires** is solid and it is the most useful thing this
project has produced about the ecosystem. The classification of **what is readable** is not, and
the difference matters more than any of the numbers.

## 1. The readable column answers a question its source cannot answer

Every `Q1 readable?` cell was filled in from the install templates. **The templates do not
contain that information.** Whether a device exposes `ro.boot.flash.locked` is a property of the
firmware the manufacturer shipped, not of the page describing how to flash it. The wiki is
silent on it.

**And the one device where it can be checked says no.** `a5xelte`, the Samsung Galaxy A5 2016 on
Ranaji's desk, is `install_method: samloader_rs` in this very catalogue, which the table marks
readable. Both captures of it in `data/contributions/rana-2026-08-29-rerun.jsonl` come back:

```
bootloader_state   unknown
partition_scheme   unknown
```

It exposes neither property. The Nothing Phone in the same run returns `locked` and
`virtual_A/B`, so the capture works; the Samsung simply does not answer.

This is the same defect class this repository keeps finding, arriving this time in research
rather than code: a confident answer drawn from a source that does not contain it. The fix is not
to redo the work. It is to **split the table in two**: what the unlock requires, which the
templates genuinely document, and what a device exposes, which only hardware can tell us. The
second is a hypothesis with 737 rows and exactly one observation against it.

## 2. That turns the tester programme from coverage into an experiment

Every captured phone answers "does this device expose the property" for one more row. The device
matrix stops being a coverage exercise and becomes the instrument that tests a stated hypothesis
about 737 devices. That is a considerably better argument for the tester programme than a target
number, and it is one a reviewer can see the shape of.

**It also means the 68 percent figure must not be quoted yet.** 498 of 737 devices are *claimed*
readable; one has been checked and it failed. Quote what the unlock requires, which is verified.
Do not quote readability until devices have been captured.

## 3. Three corrections to the numbers

**a. `ships-unlocked` is not a `command` method.** Splitting them: `command` is
`fastboot_nexus` 170 + `fastboot_nubia` 6 + `fastboot_oppo` 4 = **180**; `ships-unlocked` is
`fastboot_unlocked` 12 + `fastboot_generic` 3 = **15**. They total the 195 reported, but they
are different verdicts: "run this command" versus "there is nothing to do".

**b. "read lock state for ~74%" is wrong.** 74 percent is the share that cannot be fully
decided (542 of 737). The claimed-readable share is 180 + 15 + 303 = 498, which is **68
percent**, and per section 1 it is unverified.

**c. `proprietary-mode` conflates execution with verification, and it matters for 112 devices.**
Flashguard never executes anything. It reads a fingerprint captured from a device running normal
Android and then reasons about it. A Samsung's Download Mode is how flashing happens; it has no
bearing on what can be read beforehand. So `samloader_rs` devices are not unreadable by
construction — they read like any Android phone, and whether they answer is the open question in
section 1. The genuinely different cases are `apx` 10, `nintendo` 8, `amlogic_update` 8 and
`edl_custom` 2: single-board computers, a games console and TV boxes, 28 devices, where standard
Android properties may not exist at all.

## 4. What is solid, and what it is worth

- **737 of 737 declare `install_method`.** Verified twice, independently.
- **303 devices are vendor-gated**: a vendor account, a web portal, a token, or a waiting period
  stands between the owner and an unlock. Xiaomi's Chinese HyperOS path requires passing a timed
  community test and identity verification. No tool reading a phone can ever know whether its
  owner has done any of that, because the evidence is in someone else's database.
- **Zero wildcards in `models:`**, across all 495 files that declare it. Every model code is an
  exact string. The conservative variant-matching rule is safe on this corpus.
- **The eight dead fields are confirmed**, and independently re-verified for this analysis.

The vendor-gated number is the one to build the argument on. It is verified, it is checkable by a
reviewer in an afternoon, and it describes a boundary on the entire category of tool rather than
a gap in ours.

## 5. One correction the research made to its own brief, and it was right

The brief asserted four templates read `custom_unlock_cmd` and implied all four had devices
setting it. `fastboot_oppo` reads the field and **zero** devices set it. That is an unused
template branch rather than dead data, which is a different and smaller thing. Confirmed here.
