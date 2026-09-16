# Research Task 3: Variant Danger Findings

**Date:** 2026-09-16
**Objective:** Settle whether `product_device` hides differences across models sharing a codename that present hardware damage or bricking risks, and evaluate the architectural options for the `variant` concept in the verifier.
**Method:** Static audit of the pinned LineageOS wiki repository (737 device configuration files in `_data/devices/`, Jekyll templates in `_includes/templates/`, and documentation in `pages/`), OpenAndroidInstaller repository (`assets/configs/` and `installer_config.py`), and documented device architecture and partition mechanics across major vendor ecosystems (Samsung, Motorola, Xiaomi, OnePlus, LG, Sony, HTC, Nintendo).
**Licensing:** All descriptions and analyses are original. No third-party template text, instruction prose, or YAML is reproduced verbatim.

---

## 1. Verified Baseline Numbers

The initial audit against the pinned LineageOS clone confirmed and expanded upon the baseline counts:

| Metric | Count | Context / Source |
|---|---|---|
| Total device configs in `_data/devices/` | 737 | Full LineageOS wiki dataset |
| Devices declaring a `models:` list | 493 | Standard `ro.product.model` string declarations |
| Devices with >1 model under one file | 268 | Multi-model single-file declarations (e.g. `a5xelte`, `klte`) |
| Base codenames split into `_variant*.yml` | 89 | 220 separate files (e.g. `alioth_variant1..3`, `Mi439_variant1..4`) |
| Devices with per-variant firmware prerequisites | 44 | Defined in `before_install_device_variants` |
| Devices with firmware update templates iterating on models | 113 | Iterates through `device.models` for model-specific firmware |
| Devices with model-specific bootloader requirements | 10 | Defined in `required_bootloader` with per-model version strings |
| Models appearing across multiple codenames / files | 55 | Overlapping model strings across distinct config entries |

---

## 2. Q1: Upstream Differentiation Across Models Sharing a Codename

Where two or more models share a base codename, upstream sources systematically differentiate them across five primary structural patterns:

### Pattern 1: Split Variant Configuration Files (89 Base Codenames, 220 Files)
Upstream explicitly splits 89 device families into separate `_variant*.yml` files rather than treating them as interchangeable:
- **SoC Discrepancies:** Lenovo Vibe K5 / K5 Plus (`A6020_variant1` vs `A6020_variant2`) share model designations (`A6020a40`, `A6020a41`, etc.) but house different system-on-chip architectures (Qualcomm Snapdragon 415 MSM8929 vs Snapdragon 616 MSM8939v2).
- **Regional & Hardware Discrepancies:**
  - `alioth`: Variant 1 (POCO F3 EEA, `M2012K11AG`), Variant 2 (Redmi K40 China, `M2012K11AC`), Variant 3 (Mi 11X India, `M2012K11AI`).
  - `davinci`: Variant 1 (Mi 9T Global, `M1903F10G`), Variant 2 (Redmi K20 China, `M1903F10A`/`M1903F10C`), Variant 3 (Redmi K20 India, `M1903F10I`).
  - `lmi`: Variant 1 (POCO F2 Pro, `M2004J11G`), Variant 2 (Redmi K30 Pro, `M2001J11C`), Variant 3 (Redmi K30 Pro Zoom Edition, `M2001J11C`/`M2001J11E`).
  - `mh2lm`: LG G8X ThinQ European models (`LM-G850EM`/`LM-G850EMW`) vs North American models (`LM-G850QM`/`LM-G850UM`) vs Korean V50S ThinQ (`LM-V510N`).

### Pattern 2: Per-Model Firmware Prerequisites (`before_install_device_variants`)
In 44 device configurations, upstream supplies distinct stock firmware download links tailored to each specific model:
- `miatoll` (6 variants): POCO M2 Pro (`M2003J6CI`, board `gram`), Redmi Note 9S (`M2003J6A1G`/`M2003J6A1R`, board `curtana`), Redmi Note 9 Pro Global (`M2003J6B2G`, board `joyeuse`), Redmi Note 9 Pro India (`M2003J6A1I`, board `curtana`), Redmi Note 9 Pro Max (`M2003J6B1I`, board `excalibur`), and Redmi Note 10 Lite (`2109106A1I`, board `curtana`). Each variant requires flashing a distinct OEM stock firmware package (`miui_GRAM`, `miui_CURTANA`, `miui_JOYEUSE`, `miui_EXCALIBUR`).

### Pattern 3: Model-Indexed Stock Firmware Updates (113 Devices)
113 Samsung devices (spanning Exynos 9820, Exynos 9825, SM7125, SM7325, and SM8250 platforms) utilize firmware update templates that iterate over `device.models`. Samsung stock firmware packages from OEM update servers are strictly indexed by `product_model` (e.g. `SM-A525F`, `SM-A528B`, `SM-S901B`). Flashing a mismatched model archive fails signature verification in Odin/Heimdall or causes partition layout corruption.

### Pattern 4: Per-Model Bootloader Version Requirements (`required_bootloader`)
10 device configurations enforce exact bootloader versions conditioned on the specific model string:
- Samsung Galaxy S3 Neo (`s3ve3gjv`, `s3ve3gxx`): `GT-I9301I` requires bootloader version `I9301IXCUARA1`, whereas `GT-I9301Q` requires `I9301QXXUAHN1`.
- Samsung Galaxy Grand 2 (`ms013g`): `SM-G7102` enforces `G7102DDSBQF1`.

### Pattern 5: Explicit Template Warnings and Carrier Exclusions
- **Motorola Moto Z2 Force (`nash`):** The install template carries an explicit warning stating that flashing firmware not intended for the specific model/carrier variant (`XT1789-02` through `XT1789-07`) carries a high probability of damaging the device.
- **HTC 10 (`pme`):** The template explicitly warns that Sprint and Verizon CDMA variants are unsupported due to firmware incompatibilities, even when bootloader-unlocked, and will fail on Developer Edition builds.
- **Carrier-Branded OnePlus / Realme / Oplus:** Templates (`firmware_update_oneplus_fastbootd.md`, etc.) explicitly warn that instructions do not apply to carrier-branded models (such as T-Mobile single-SIM variants vs Global dual-SIM variants).
- **Nintendo Switch (`nx`):** Exploitability branches strictly on the hardware model identifier on the chassis (`HAC-001` unpatched V1 vs `HAC-001(-01)` patched V2 / Lite / OLED).

---

## 3. Q2: Documented Damage and Hardware Failure Modes

Cross-flashing builds or firmware across models sharing a single `product_device` codename produces four well-documented classes of damage:

### 1. Baseband, NVRAM, and IMEI Destruction
- **Samsung Galaxy S5 (`klte` family):** `klte` encompasses international GSM models (`SM-G900F`, `kltexx`) alongside US carrier models (`SM-G900V` Verizon, `SM-G900P` Sprint, `SM-G900T` T-Mobile). Flashing GSM baseband or modem binaries onto CDMA/carrier hardware corrupts the `efs` partition, zeroes out the IMEI, or induces modem crash loops (`SECURE CHECK FAIL : MODEM`).
- **Motorola Radio Partitions (`nash`, `clark`):** Cross-flashing radio firmware across XT model variants corrupts the non-volatile memory partitions (`modemst1`, `modemst2`), erasing hardware RF calibration and resulting in an unrecoverable `Baseband: Unknown` state.
- **OnePlus Carrier Variants (`guacamole` GM1915 vs GM1913/GM1917):** T-Mobile variants feature a single-SIM physical tray, differing modem NVRAM configurations, and carrier-specific partition tables. Flashing generic global images without converting parameter partitions can lead to loss of cellular service or force the SoC into Qualcomm Emergency Download (EDL / 9008) mode.

### 2. Camera and Peripheral Hardware Incompatibilities
- **Samsung Galaxy S3 Neo (`s3ve3gjv` vs `s3ve3gxx`):** The `GT-I9301I` revision incorporates a Samsung S5K4H5YB camera sensor, while the `GT-I9301Q` revision uses a Sony IMX175 sensor. Cross-flashing kernel and vendor blobs breaks camera initialization at the HAL level.
- **Xiaomi Redmi Note 9 Series (`miatoll`):** `curtana` (Redmi Note 9S) features a 48MP main sensor and lacks NFC hardware; `joyeuse` (Redmi Note 9 Pro) features a 64MP sensor and includes NFC. Cross-flashing vendor trees produces non-functional cameras and NFC driver panics.

### 3. Anti-Rollback (ARB) and Bootloader Hard-Bricks
- **LG V30 (`joan` vs `H932`):** T-Mobile model `H932` uses different RSA root signing keys and Anti-Rollback fuse definitions compared to open-market `US998` and `H930` models. Attempting standard cross-flashing procedures on `H932` blows ARB fuses and results in a permanent Qualcomm EDL 9008 hard-brick requiring hardware board replacement.
- **Xiaomi Regional Firmware Mismatches:** Flashing a Global or EEA ROM on a Chinese hardware model (or vice versa) while locking or updating the bootloader triggers Qualcomm ARB enforcement and boot loops.

### 4. Partition Table (PIT) Corruption
- On Samsung devices, regional variants within the same codename (e.g. `SM-A510F` vs `SM-A510M` in `a5xelte`) occasionally possess differing partition table geometries. Flashing an incompatible PIT partition or firmware archive triggers Odin write failures and unbootable states.

---

## 4. Q3: Risks of Retaining `variant` as a Wording-Only Placeholder

If the recipe schema retains the `variant` field while only altering its reason string to avoid implying a device read error, three specific risks remain:

1. **Perpetual False Abstention:**
   Device captures (via both USB descriptor parsing in `01-detect.sh` and ADB properties in `02-android.sh`) produce `product_device` (`ro.product.device`) and `product_model` (`ro.product.model`). Neither interface outputs a field called `variant`. Consequently, any recipe containing `variant` will indefinitely return `cannot-verify`, reducing the actionable output of the verifier.
2. **Obscuring the Actual Discriminator:**
   The concrete discriminator collected from hardware and published by upstream projects is `product_model`. Calling the check `variant` hides the source property and prevents automated verification against real model strings.
3. **Encouraging Flawed Downstream Wiring:**
   Retaining a vague, unpopulated placeholder creates a trap where future contributors may attempt to wire unrelated fields (such as how `identity_source` was previously misinterpreted as variant validation) to satisfy the check.

---

## 5. Evidence for the Three Architectural Options

The evidence for each potential ruling is summarized below without making a final policy determination:

### Option A: Drop `variant` entirely, relying solely on `product_device`
- **Evidence For:**
  - Simplifies recipe schema to match what minimal Android properties provide.
  - Many device trees share identical unified kernel/AOSP binaries under a single `product_device`.
  - Eliminates artificial `cannot-verify` verdicts caused by a missing placeholder.
- **What it would take to be wrong:**
  - A device reporting matching `product_device` but an unsupported carrier/regional `product_model` is flashed with a recipe that bricks its modem, destroys its IMEI, or blows ARB fuses (as seen with `nash`, `klte`, `H932`, and `miatoll`). Relying solely on `product_device` would produce a `safe` verdict where the action is actually hazardous.

### Option B: Replace `variant` with an explicit `supported_models` allowlist (evaluated against `product_model`)
- **Evidence For:**
  - Upstream publishes `models:` lists for 493 of 737 devices, and OpenAndroidInstaller specifies explicit discrete strings in `supported_device_codes`.
  - The fingerprinting tools already capture `product_model` (`ro.product.model`) in real runs (e.g. `SM-A510F` on `a5xelte`, `A063` on `Spacewar`).
  - Allows the verifier to make a deterministic `safe` or `unsafe` decision based on exact hardware identity.
- **What it would take to be wrong:**
  - Recipe maintainers fail to populate complete model lists, causing false `unsafe` or `cannot-verify` verdicts on valid but unlisted hardware variants.
  - Fingerprint capture in restricted environments (e.g. raw fastboot / recovery without model properties) cannot supply `product_model`.

### Option C: Retain `variant` as an optional informational field with wording clarification
- **Evidence For:**
  - Preserves backward compatibility with existing v0.1 JSON recipe structures.
  - Conservatively abstains (`cannot-verify`) whenever a recipe flags variant sensitivity, preventing automated execution on ambiguous targets.
- **What it would take to be wrong:**
  - The verifier permanently abstains on multi-model devices despite having the exact `product_model` data in the fingerprint needed to resolve the check safely.
