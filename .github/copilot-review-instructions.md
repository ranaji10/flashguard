# Code review instructions — Flashguard

Flashguard decides whether a provisioning recipe is safe for a specific device, without
executing it. A wrong "safe" can brick someone's phone.


### Never run these (copied verbatim from CLAUDE.md)

`tests/check-rule-agreement.sh` fails the build if this block differs from CLAUDE.md.
Edit CLAUDE.md first, then copy the block here unchanged.

    fastboot flashing unlock      fastboot oem unlock
    fastboot flash ...            fastboot erase ...
    fastboot format ...           fastboot update ...
    fastboot set_active ...       adb disable-verity
    dd ...

## Review priorities, in order

1. **False-safe pathways.** Any change that could make an uncertain result read as certain
   is the most serious defect possible here. Missing evidence must stay `unknown`, never
   become a confident default.
2. **Purity.** `classify.sh`, `derive.sh` and the verifier take text in and return a result.
   Flag any device I/O, network call, filesystem read or global state added to them.
3. **Read-only.** Nothing may write to, flash, erase or unlock a device. Flag `fastboot
   flash|erase|format|oem|flashing`, `adb root|remount|disable-verity`, `dd`, `mkfs`.
4. **Privacy.** Serial numbers, IMEI, IMSI, MAC addresses, ICCID and Android ID must never
   be read or stored. Flag `getprop` without an explicit allowlist, `adb devices` (prints
   the serial; use `adb get-state`), and any unfiltered `lsusb -v` that keeps `iSerial`.
5. **Portability.** Shell must run on **bash 3.2** — macOS ships it. Flag `declare -A`,
   `mapfile`, `readarray`, `${v,,}`, `${v^^}`, `coproc`, `;;&`, `&>>`.

## Specific traps this project has already hit

- Reading only the first USB interface. Phones are composite devices; ADB sits after MTP.
- `grep -A2` across a descriptor, which pairs a class from one interface with a protocol
  from another. Walk interfaces properly.
- Inferring a partition scheme from an absent property. Absent is not `single`.
- Treating a classifier's own answer as ground truth in a test fixture.

## Style

- No machine-learning vocabulary. Nothing here is trained or inferred.
- Comments explain **why**, especially why a defensive check exists. Do not add comments
  that restate the code.
- Errors tell the person what to do next, not just what failed.
- Prefer abstaining and saying so over guessing.
