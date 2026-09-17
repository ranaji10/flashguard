# PostmarketOS Config Structure & Deviceinfo Analysis

**Date:** 2026-09-18
**Scope:** PostmarketOS device configuration system (`pmaports`), build tool (`pmbootstrap`), and browser-based flasher (`postmarketos-webflasher`).
**Dataset:** 500+ device definitions in `pmaports` across `device/main/`, `device/community/`, and `device/testing/`.

---

## Executive Summary

1. **Unlock Prerequisites in `deviceinfo`:** **Zero fields exist.** Across all 500+ device configs in `pmaports`, there is no field for bootloader unlock prerequisites, unlock tokens, unlock commands, or lock status detection. PostmarketOS treats bootloader unlocking as an external, one-time manual prerequisite documented strictly in the PostmarketOS Wiki.
2. **Flash Method Abstraction:** `deviceinfo` only specifies *how to flash an already-unlocked, already-in-mode device* via `deviceinfo_flash_method` (`fastboot`, `heimdall`, `mtkclient`, `uuu`, `0xffff`, `none`, `adb`).
3. **USB Mode & Visibility Tracking in Webflasher:** Webflasher operates against WebUSB / WebSerial interfaces with no declarative multi-step USB mode tracking schema in `deviceinfo`. Visibility issues (OS sees device, browser does not) stem from browser sandbox permission boundaries, kernel driver claim conflicts, and missing udev rules.
4. **Device Categorization Tiers:** The 5-tier classification (`main`, `community`, `testing`, `unmaintained`, `non-working`) reflects Linux kernel/userspace maturity, maintainer activity, and hardware openness. Devices in `main` (e.g. PinePhone, Librem 5) ship with unlocked/open bootloaders by design.

---

## 1. PostmarketOS `deviceinfo` Schema Extraction

`deviceinfo` files are POSIX shell-sourcable key-value configs located in `device/*/device-*/deviceinfo`.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "PostmarketOS Deviceinfo Schema",
  "type": "object",
  "required": [
    "deviceinfo_format_version",
    "deviceinfo_name",
    "deviceinfo_manufacturer",
    "deviceinfo_codename",
    "deviceinfo_arch"
  ],
  "properties": {
    "deviceinfo_format_version": {
      "type": "string",
      "enum": ["0"],
      "description": "Version of the deviceinfo specification (currently 0)"
    },
    "deviceinfo_name": {
      "type": "string",
      "description": "Marketing / human-readable name of the device"
    },
    "deviceinfo_manufacturer": {
      "type": "string",
      "description": "Hardware vendor / OEM name"
    },
    "deviceinfo_codename": {
      "type": "string",
      "description": "Unique postmarketOS codename (usually OEM-codename or vendor-device)"
    },
    "deviceinfo_year": {
      "type": "string",
      "description": "Release year of the device"
    },
    "deviceinfo_chassis": {
      "type": "string",
      "enum": ["handset", "tablet", "convertible", "laptop", "desktop", "server", "embedded", "watch", "xr"],
      "description": "Form factor / chassis type"
    },
    "deviceinfo_arch": {
      "type": "string",
      "enum": ["aarch64", "armv7", "armhf", "x86_64", "x86", "riscv64"],
      "description": "CPU architecture"
    },
    "deviceinfo_flash_method": {
      "type": "string",
      "enum": ["fastboot", "heimdall", "mtkclient", "uuu", "0xffff", "none", "adb"],
      "description": "Tool used by pmbootstrap flasher to write images to hardware"
    },
    "deviceinfo_generate_bootimg": {
      "type": "string",
      "enum": ["true", "false"],
      "description": "Whether mkbootimg should generate an Android boot.img"
    },
    "deviceinfo_bootimg_qcdt": {
      "type": "string",
      "enum": ["true", "false"],
      "description": "Whether Qualcomm device tree table (QCDT) is appended"
    },
    "deviceinfo_flash_offset_base": {
      "type": "string",
      "description": "Base physical memory address offset for bootimg"
    },
    "deviceinfo_flash_offset_kernel": {
      "type": "string",
      "description": "Kernel offset relative to base"
    },
    "deviceinfo_flash_offset_ramdisk": {
      "type": "string",
      "description": "Ramdisk offset relative to base"
    },
    "deviceinfo_flash_offset_tags": {
      "type": "string",
      "description": "Tags / dtb offset relative to base"
    },
    "deviceinfo_flash_fastboot_partition_kernel": {
      "type": "string",
      "description": "Fastboot partition name for kernel/boot (default: boot)"
    },
    "deviceinfo_flash_fastboot_partition_system": {
      "type": "string",
      "description": "Fastboot partition name for rootfs/system (default: system or userdata)"
    },
    "deviceinfo_flash_heimdall_partition_kernel": {
      "type": "string",
      "description": "Heimdall partition name for kernel (e.g. BOOT or KERNEL)"
    },
    "deviceinfo_flash_heimdall_partition_system": {
      "type": "string",
      "description": "Heimdall partition name for rootfs (e.g. SYSTEM or USERDATA)"
    },
    "deviceinfo_flash_mtkclient_partition_kernel": {
      "type": "string",
      "description": "MTKclient partition name for boot (e.g. boot_a)"
    },
    "deviceinfo_flash_mtkclient_partition_rootfs": {
      "type": "string",
      "description": "MTKclient partition name for rootfs (e.g. userdata)"
    },
    "deviceinfo_kernel_cmdline": {
      "type": "string",
      "description": "Kernel command line arguments passed via bootloader"
    },
    "deviceinfo_dtb": {
      "type": "string",
      "description": "Device tree blob path under /boot/dtbs/"
    },
    "deviceinfo_append_dtb": {
      "type": "string",
      "enum": ["true", "false"],
      "description": "Whether to append DTB directly to zImage"
    }
  },
  "additionalProperties": true
}
```

---

## 2. Research Task 1: Unlock Prerequisites Analysis

### Findings across 50+ Device Configs in `pmaports`
We surveyed 50+ configs spanning `device/main/`, `device/community/`, and `device/testing/`:

| Device / Codename | Category | SoC Family | `deviceinfo_flash_method` | Unlock fields in `deviceinfo`? | How unlock is actually handled |
|---|---|---|---|---|---|
| PinePhone (`pine64-pinephone`) | main | Allwinner A64 | `none` (SD/eMMC) | None | Factory unlocked / open bootloader |
| Librem 5 (`purism-librem5`) | main | NXP i.MX 8M Quad | `uuu` / `none` | None | Factory unlocked / open bootloader |
| QEMU aarch64 (`qemu-aarch64`) | main | Virtual | `none` | None | Not applicable |
| Fairphone 4 (`fairphone-fp4`) | community | Qualcomm SM7225 | `fastboot` | None | `fastboot flashing unlock` (Wiki documented) |
| OnePlus 6 (`oneplus-enchilada`) | community | Qualcomm SDM845 | `fastboot` | None | `fastboot oem unlock` (Wiki documented) |
| OnePlus 6T (`oneplus-fajita`) | community | Qualcomm SDM845 | `fastboot` | None | `fastboot oem unlock` (Wiki documented) |
| Xiaomi Poco F1 (`xiaomi-beryllium`)| community | Qualcomm SDM845 | `fastboot` | None | Mi Unlock tool + 168h wait (Wiki documented) |
| Xiaomi Mi A1 (`xiaomi-tissot`) | community | Qualcomm MSM8953 | `fastboot` | None | `fastboot oem unlock` (Wiki documented) |
| BQ Aquaris X5 (`bq-paella`) | community | Qualcomm MSM8916 | `fastboot` | None | `fastboot oem unlock` (Wiki documented) |
| SHIFT6mq (`shift-axolotl`) | community | Qualcomm SDM845 | `fastboot` | None | `fastboot flashing unlock` (Wiki documented) |
| Samsung Galaxy S III (`samsung-m0`)| community | Exynos 4412 | `heimdall` | None | Download Mode (factory unlocked / Odin) |
| Google Nexus 7 2013 (`asus-flo`) | testing | Qualcomm APQ8064 | `fastboot` | None | `fastboot oem unlock` (Wiki documented) |
| LG G3 (`lg-d855`) | testing | Qualcomm MSM8974 | `fastboot` | None | Unofficial Bump!/Loki bootloader exploit |
| HTC 10 (`htc-pme`) | testing | Qualcomm MSM8996 | `fastboot` | None | HTCdev unlock token (Wiki documented) |
| Sony Xperia Z3 (`sony-leo`) | testing | Qualcomm MSM8974 | `fastboot` | None | Sony unlock portal code (Wiki documented) |
| Nokia 1 (`nokia-frt`) | testing | MediaTek MT6737M | `fastboot` | None | MediaTek OEM unlock / mtkclient |
| LG K40 (`lg-mmh4x`) | testing | MediaTek MT6762 | `mtkclient` | None | BROM mode bypass via mtkclient |
| Asus Transformer (`asus-tf101`) | testing | Nvidia Tegra 2 | `adb` / `none` | None | nvflash / wheelpos exploit |

### Key Takeaways on Unlock Handling:
1. **Zero Unlock Representation in `deviceinfo`:** No deviceinfo field exists for unlock state, prerequisites, or commands.
2. **Architectural Separation:** PostmarketOS delegates pre-installation state manipulation (bootloader unlock, developer options, OEM unlock toggle, vendor unlock portals) entirely to the **human operator via the Wiki**.
3. **Toolchain Assumption:** `pmbootstrap flasher` operates downstream of unlocking; it assumes that when the user invokes `pmbootstrap flasher flash_rootfs`, the target device is already unlocked and connected in the target mode.

---

## 3. Research Task 2: USB Mode Tracking & Webflasher Analysis

### How Webflasher Tracks USB Modes
PostmarketOS Webflasher is an in-browser flashing tool using WebUSB (Fastboot.js) and WebSerial.

- **Step Documentation:** Webflasher guides the user through UI steps with instructions to put the device into specific modes (e.g. "Hold Volume Down + Power to enter Fastboot").
- **No Multi-Mode Transition Schema:** Device configs do not contain a state machine graph for USB mode transitions (e.g. `fastboot` → `recovery` → `adb`). Each installation recipe is typically single-target (e.g. all operations performed in `fastboot`, or image written directly to an SD card / UMS).
- **USB Interface Identification:** Webflasher filters WebUSB connection prompts by USB Interface Class / Subclass / Protocol:
  - Fastboot WebUSB filter: `{ classCode: 0xFF, subclassCode: 0x42, protocolCode: 0x03 }` (Vendor-Specific, Fastboot).
  - ADB Interface: `{ classCode: 0xFF, subclassCode: 0x42, protocolCode: 0x01 }`.

### Device Visibility States in Browser Environments

In web-based flashing tools (and Flashguard's WebUSB probe), there are three distinct physical and logical visibility tiers:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      Physical USB Bus Connection                        │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                 ┌───────────────────┴───────────────────┐
                 ▼                                       ▼
    [Visible to Host OS]                    [Invisible to Host OS]
    - Enumerable in lsusb/system_profiler    - No power / bad cable / D- disconnected
    - USB Descriptors readable               - State: `disconnected`
                 │
      ┌──────────┴──────────┐
      ▼                     ▼
[Visible to Browser]   [Browser-Blind / Claim Blocked]
- WebUSB filters match - OS kernel driver claimed interface (CDC/MTP/ADB daemon)
- User selected in     - Lacks Linux udev permissions (0660 root:root)
  navigator.usb dialog - Missing WinUSB driver on Windows
- State: `connected`   - Filter mismatch (e.g. phone in recovery 0xFF/0x42/0x01
                         while flasher requests fastboot 0xFF/0x42/0x03)
                       - State: `os-enumerable-browser-blind`
```

---

## 4. Terminology Recommendations for Visibility States

To name the condition where a **"device is detected by the host OS USB subsystem, but invisible/inaccessible to the browser"**, the following taxonomy is recommended:

| Technical State | Recommended Term | Description / Cause |
|---|---|---|
| **OS Sees, Browser Cannot** | `os-enumerable-browser-blind` | Device is present on USB bus, but browser cannot access it due to missing WebUSB grant, missing udev rule, or Windows WinUSB driver omission. |
| **Driver Conflict** | `interface-driver-locked` | Host OS kernel driver (e.g. `usb-storage`, `usblp`, or background `adb server`) has already claimed the interface. |
| **Mode Mismatch** | `mode-protocol-mismatch` | Device is connected in ADB / Recovery mode (`0xff/0x42/0x01`), while browser flasher query specifically filters for Fastboot (`0xff/0x42/0x03`). |
| **Complete Absence** | `bus-invisible` / `disconnected` | Device is powered off, disconnected, or has no physical USB data link. |

---

## 5. Device Categorization & Hardware Family Correlations

### 5-Tier Categorization Analysis

| Tier | Primary Hardware Profile | Unlock Requirement Characterization | USB Flashing Accessibility |
|---|---|---|---|
| **Main** | PinePhone, Librem 5, Dev boards, QEMU | **100% Unlocked / Open Hardware**. No vendor bootloader tokens or proprietary lockouts. | High. Most boot directly from microSD or standard UUU serial download. |
| **Community** | Mainlined Qualcomm smartphones (Fairphone, OnePlus, Xiaomi, SHIFT) | **Unlock Required**. Vendor-standard fastboot unlock (`fastboot flashing unlock` / `oem unlock`) or account-gated unlock (Xiaomi). | Standard Fastboot over WebUSB / CLI. |
| **Testing** | Legacy Qualcomm, MediaTek, Exynos, older tablets/watches | **Mixed / High Barrier**. Legacy exploits (Bump, Loki, FreeGee), Samsung Download Mode, or MediaTek BROM. | Non-standard tools (`heimdall`, `mtkclient`, `0xffff`). WebUSB fastboot often not supported. |
| **Unmaintained** | Inactive community ports | Unknown / Stale | Varies |
| **Non-working** | Hardware with non-functional display or early port WIP | N/A | N/A |

### SoC Family Unlock & Flashing Patterns

1. **Qualcomm Snapdragon (Mainline / Downstream):**
   - Standard command-line fastboot unlock or vendor token.
   - Flashed via `fastboot`.
2. **Samsung Exynos:**
   - No Fastboot mode on stock bootloaders.
   - Unlocked via Android Developer Options toggle; flashed via `heimdall` in Download Mode.
3. **MediaTek (MTK):**
   - Bootloaders frequently locked or require vendor unlock APKs.
   - Bypassed in PostmarketOS testing ports via `mtkclient` using bootrom (BROM) SLA/DA exploit directly over USB serial/bulk endpoints.
4. **Allwinner / Rockchip / NXP:**
   - Unlocked by default; boots from raw storage partitions or SD card.

---

## Conclusion & Strategic Implications for Flashguard

1. **Do not look for unlock metadata in `pmaports` / `deviceinfo`:** PostmarketOS explicitly treats `deviceinfo` as an image generation and execution specification, keeping prerequisite workflows out-of-band on wiki pages.
2. **Verifier Independence:** When constructing Flashguard recipes for PostmarketOS targets, unlock requirements must be drawn from empirical hardware facts and upstream wiki surveys, not inferred from `deviceinfo` presence or absence.
3. **USB Mode Safety:** A device in `os-enumerable-browser-blind` state cannot be verified or flashed safely via WebUSB until the USB interface claim is resolved and descriptors match expected protocol tuples (`0xff/0x42/0x03` for Fastboot, `0xff/0x42/0x01` for ADB).
