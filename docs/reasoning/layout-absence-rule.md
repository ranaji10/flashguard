# The layout absence rule, 17 October 2026

*Asked for by Ranaji after the round 3 review (`Claude outputs/flashguard-round3-review-2026-10-17.md`,
outside the repo), once the research below was done. Widened the same evening, at his request,
from Android 8+ to every Android version. Held by `tests/test_absence_rule_2026_10_17.py`:
undo any part of the rule and a test there fails.*

## The rule

No Android property ever says "this phone has one set of partitions". A phone with A/B slots
says so through three markers. The verifier reads the layout as **single** when, and only when:

1. `derive.sh` queried all three markers and all three were empty
   (`partition_basis` is exactly the "no ab_update, no slot_suffix, no virtual_ab" text), and
   `slot_suffix` is empty;
2. the firmware is the maker's own (`firmware_origin` is `stock`);
3. the build is a `user` build signed with `release-keys` (from `build_type` and `build_tags`,
   or from the end of the build fingerprint on captures made before kit 2026-10-08);
4. the phone's Android version was read (`sdk` is a number). Any version qualifies; see
   "Widened to every Android version" below.

Outside that scope the verifier abstains exactly as before. A reported layout is never
overridden. The rule exists only in recipe formats v0.2 and v0.3; v0.1 is unchanged.

The inference has its own reason codes, so every result says when it was used:
`match-partition_scheme-inferred-single` (pass) and `partition-scheme-mismatch-inferred` (unsafe).

## Why the absence means something

The three markers come from three different places, and a working A/B phone has all of them:

| Marker | Who writes it | Source |
|---|---|---|
| `ro.build.ab_update` | The build system, whenever `AB_OTA_UPDATER` is defined, which every A/B target must set to true | AOSP `core/sysprop_config.mk`; AOSP "Implement A/B updates" |
| `ro.boot.slot_suffix` | The bootloader, on every boot of an A/B phone (kernel command line, bootconfig or device tree) | AOSP "Implement A/B updates" |
| `ro.virtual_ab.enabled` | The build, on virtual A/B phones | AOSP virtual A/B |

A stock A/B phone missing all three would be a build that cannot update itself. The scope
limits exist because the same is not true of custom builds (a ROM writes its own properties)
or of debug builds.

`dynamic_partitions`, `treble_enabled` and `first_api_level` were added to the kit on 8 October
in the hope of a positive single signal. Round 3 showed none of them gives one: phones with no
A/B marker report `dynamic_partitions=true` (A52s, Titan Pocket, OnePlus IV2201, vivo V2307),
launch levels 30 to 33, and Treble enabled. They are kept as records, not used by the rule.
No phone has ever set `ro.build.ab_update=false`; the property is simply absent on non-A/B builds.

## Widened to every Android version

The first version applied from Android 8 (SDK 26), because that was where the labelled
evidence sat. Ranaji asked to widen it to Android 7 (SDK 24 and 25), and whether older versions
make sense too. They do, and on firmer ground than the rest:

- **Android 7.x.** AOSP's A/B FAQ says the platform code "is public in Android 7.1 and higher",
  and that "Pixel and Pixel XL phones from October 2016 shipped with A/B" (they launched on 7.1).
  A stock 7.x A/B phone carries the markers like any later one. Two
  captured stock 7.0 phones with upstream labels, the Galaxy A5 2016 and the LG G4, are
  non-A/B upstream and show no marker.
- **Android 6 and older.** No public A/B implementation existed before 7.1 and no A/B phone
  shipped before the Pixel, so a phone running the maker's own Android 6 or older cannot be
  expected to have slots. Here the absence is barely needed as evidence; the rule still
  requires it, so a contradiction would show.

The firmware conditions stay: a custom ROM can be newer than the phone and can write anything.

## Reads from a shell on the phone

A record whose properties were read in a terminal on the phone itself (`capture_route:
device_shell`, `data/schema.md`) runs as an app, not as the adb shell user. Whether an app sees
every A/B marker is not established, so such a record carries its own `partition_basis` and
the rule never fires on it.

## Evidence, against upstream labels

Upstream labels come from LineageOS (`is_ab_device`, and a `recovery` partition) and
OpenAndroidInstaller (`is_ab_device: true/false`), local clones of 7 September 2026.

| Group | Phones | Agree with the phone |
|---|---|---|
| Android 8+, stock, upstream says not A/B | Galaxy A52s, Galaxy S9+, Huawei P smart (LineageOS); Galaxy S8 (OpenAndroidInstaller) | **4 of 4** read as single |
| Android 8+, stock, labelled from other public sources (see below) | Galaxy S8+, Galaxy J5 2017, Lenovo K10 Note, OnePlus Nord CE 2 (IV2201) | **4 of 4** read as single |
| Android 7.0 and older, upstream says not A/B | Galaxy A5 2016, LG G4, Nexus 5, Droid 4 (stock); Xperia X, Galaxy Note 10.1 2014 (custom, still out of scope) | 6 of 6 show no marker |
| Upstream says A/B | Nothing 1, Edge 30 Ultra, Nord CE 3 Lite, OnePlus 6T, POCO F3, Pixel 8, Nokia 7 plus | 7 of 7 report A/B positively |

### Labels from other public sources (researched 17 October)

None of these phones is in LineageOS or OpenAndroidInstaller. The labels come from the build
configuration a recovery is built from (`BoardConfig.mk`: an A/B device sets `AB_OTA_UPDATER`
and normally has no recovery partition) or from TWRP's own install instructions. Device trees
are community work, weaker than an upstream wiki, so each label names its source.

| Phone | Label | Evidence |
|---|---|---|
| Galaxy S8+ (`dream2lte`) | not A/B | Official TWRP page installs by `dd` to the `RECOVERY` partition: https://twrp.me/samsung/samsunggalaxys8plus.html |
| Galaxy J5 2017 (`j5y17lte`) | not A/B | TwrpBuilder device tree, no `AB_OTA_UPDATER`: https://github.com/TwrpBuilder/android_device_samsung_j5y17lte |
| Lenovo K10 Note (`kunlun2`) | not A/B | Official TWRP page: `fastboot flash recovery` (https://twrp.me/lenovo/lenovok10note.html); device tree has a 64 MiB recovery partition and no `AB_OTA_UPDATER` (https://github.com/GiaSen/device_lenovo_kunlun2-old/blob/ten/BoardConfig.mk) |
| OnePlus Nord CE 2 5G (IV2201, `ivan`) | not A/B | TWRP device tree: 128 MiB recovery partition, no `AB_OTA_UPDATER` (https://github.com/Ko-Hi-Dev/twrp_iv2201/blob/twrp_11-ivan/BoardConfig.mk) |
| Unihertz Titan Pocket | none found | Ubuntu Touch and GSI guides name `boot`, `vbmeta` and `super` but no slots; nothing states the layout |
| vivo Y200 5G (V2307) | none found | No custom-firmware work found; vivo offers no official unlock for most models |

All four phones with a label agree with the rule, and none of the 21 labelled captured phones
contradicts its label. Two Android 8+ phones remain unlabelled.

**Upstream labels can be wrong, in exactly the dangerous direction.** OpenAndroidInstaller's
`alioth` config says `is_ab_device: false`. LineageOS says true, and the captured POCO F3
reports virtual A/B. The phone's own report catches that, which is why the rule never
overrides a reported layout. `alioth-oai.json` keeps it as a corpus case expected `unsafe`.

## What a false single would cost

Researched before adding the rule, because the answer decides whether severity could carry
part of the argument. It cannot.

- A recipe for a single-layout phone writes `recovery`. On an A/B phone without that
  partition, fastboot refuses ("partition does not exist" or similar) and nothing is written.
  That case is harmless.
- AOSP allows A/B phones a dedicated recovery image too (LineageOS `eqs` is A/B with
  `recovery_partition_name: recovery`). There the write succeeds, and the recipe goes on without
  any slot handling.
- LineageOS adds a copy-partitions step on A/B phones because "the inactive slot can be
  unpopulated or contain much older firmware than the active slot, leading to various issues
  including a potential hard-brick". OpenAndroidInstaller uses `is_ab_device` to route add-ons
  into the newly active slot. A single-layout recipe does neither.

So a false single is a real false safe, up to a hard brick. The rule rests on the absence being
near-impossible on a working stock A/B build, not on the mistake being cheap.

## Residual risk, stated

A maker's A/B build that omits `ro.build.ab_update` and whose bootloader does not pass a slot
suffix in any form would be read as single. None is known, and none of the 21 captured phones
with a public label contradicts it. The two unlabelled Android 8+ phones (Titan Pocket, vivo Y200) are the cheapest place to look
for one.

## What it changed

| Recipe | Phone | Before | After |
|---|---|---|---|
| `a52sxq.json` | Galaxy A52s, 3 captures | cannot-verify | not-ready (locked) |
| `star2lte.json` | Galaxy S9+ | cannot-verify | not-ready (locked) |
| `figo.json` (new) | Huawei P smart | none | cannot-verify (locked, and the maker withdrew the unlock route: `unlock_route`) |
| `a5xelte.json` | Galaxy A5 2016 (Android 7.0) | layout unknown | layout single; still cannot-verify, because the phone does not report its lock state |

`alioth.json` (POCO F3, from LineageOS, not-ready) and `alioth-oai.json` (from
OpenAndroidInstaller, unsafe) do not use the rule: the phone reports its layout.

## Sources

- AOSP, Implement A/B updates: https://source.android.com/docs/core/ota/ab/ab_implement
- AOSP, A/B updates FAQ ("public in Android 7.1 and higher"; Pixel and Pixel XL of October 2016): https://source.android.com/docs/core/ota/ab/ab_faqs
- AOSP, `core/sysprop_config.mk`: https://android.googlesource.com/platform/build/+/eddacbb01f/core/sysprop_config.mk
- AOSP, Recovery images: https://source.android.com/docs/core/architecture/bootloader/recovery-images
- LineageOS wiki, copy-partitions template: https://github.com/LineageOS/lineage_wiki/blob/main/_includes/templates/device_specific/before_lineage_install_ab_copy_partitions.md
- OpenAndroidInstaller, `alioth.yaml` and `tooling.py` (`is_ab` handling): https://github.com/openandroidinstaller-dev/openandroidinstaller
