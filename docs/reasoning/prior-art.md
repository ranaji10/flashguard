# Prior art

> Scanned 26 August 2026. Figures marked *(checked)* were read from the source on
> that date and should be re-confirmed shortly before submission, since stars,
> issue counts and device counts move.

## The claim this project can defend

Not "nobody verifies provisioning recipes." That is too strong and a reviewer in
this space will know it. The defensible claim is narrower and harder to argue with:

> **Execution tooling for community firmware is mature. Verification tooling does
> not exist.** Several projects will happily run a provisioning recipe on a phone.
> None of them can tell you, before it runs, whether *this* recipe is safe for
> *this* device, and none expose that judgement as a reusable component that other
> tools can call.

Everything below either executes, or verifies for a different device class.

---

## 1. OpenAndroidInstaller — the closest existing project

<https://github.com/openandroidinstaller-dev/openandroidinstaller>

A desktop installer that walks a person through putting an alternative Android
distribution on their phone. Per-device configuration files describe the steps for
each supported model.

- **88 devices supported** across Fairphone, Google Pixel, Motorola, OnePlus,
  Samsung, Sony and Xiaomi/Poco *(checked)*
- **GPL-3.0-or-later**, originally by Tobias Sterbak, 2022 onward *(checked)*
- Actively maintained: 523 stars, 380 open issues, 16 open pull requests *(checked)*
- README states: *"This application is currently in beta state, so use at your own
  risk! While many people tested the application so far and we heard of no bricked
  devices, things might still go wrong."* *(checked)*

**Why it matters, in three separate ways.**

**As prior art.** It must be named in Q5. Omitting the closest existing project
reads either as an incomplete scan or an avoided comparison, and both cost more
than the comparison itself would.

**As the position that makes this project make sense.** OpenAndroidInstaller
*executes*. This project *verifies*. Its own safety statement is
"we heard of no bricked devices," which is a report of experience, not a property
of the system. That gap is the thesis: this project is the verification layer
underneath tools that already execute, and OpenAndroidInstaller is its most obvious
first consumer rather than its competitor.

**As a corpus.** Its 88 per-device configurations are published, structured and
GPL-licensed. They are real provisioning recipes for real devices. This is the
answer to the corpus problem: the verifier can be validated against dozens of
genuine recipes on day one without owning the corresponding hardware. Its 380 open
issues are, separately, a catalogue of real-world provisioning failure modes that
would otherwise take a year to accumulate.

> **Licence note.** GPL-3.0-or-later. If configs or derived data are used, the
> licence has to be respected and a compatible choice made for this repository.
> This is one argument for GPL-3.0-or-later here too.

---

## 2. fwupd and the Linux Vendor Firmware Service

<https://fwupd.org/>

The reference model for open firmware update infrastructure. Vendors publish
firmware to LVFS, fwupd applies it, and LVFS runs a documented firmware testing
pipeline before anything reaches users.

Closest in *spirit* to this project of anything that exists: open, community
infrastructure that puts a verification stage between a firmware artefact and a
device. It is prior art in the honest sense and should be cited approvingly.

The differences that leave room for this project:

- It covers PCs and peripherals, not the Android provisioning path.
- It verifies *vendor-submitted firmware entering a trusted pipeline*. This project
  has to judge an *arbitrary recipe of unknown provenance* against a *specific
  device's current state*, which is a different problem.
- Its safety model rests on vendor participation. Vendor-abandoned devices, by
  definition, have no participating vendor.

---

## 3. The browser and vendor flashers

| Tool | What it does | Gap |
|---|---|---|
| Google Android Flash Tool | Flashes Pixel devices from Chrome via WebUSB | Executes. Vendor devices only. No verification of third-party recipes. |
| kdrag0n's fastboot.js | WebUSB fastboot implementation | A transport library. Correctly makes no safety claim. |
| LineageOS web installer | Guided browser install for supported devices | Executes. Safety comes from per-device human curation, which is exactly the scarce resource this project is trying to stop depending on. |
| Heimdall, Odin, SP Flash Tool | Vendor and community low-level flashers | Execute. No safety model at all. |

---

## 4. /e/OS Easy Installer — the documented failure this project is about

<https://community.e.foundation/t/easy-installer-incorrectly-reports-e-os-compatibility/42475>

Worth citing specifically, in Q6 rather than Q5, because it is a real, reproducible,
documented failure of exactly the judgement this project is trying to make well.

The installer detected a Samsung Galaxy S7 edge (SM-G935F) correctly. Its supported
list held the codenames `herolte` and `hero2lte`. The device reported itself as
`hero2ltexx`. A trailing regional suffix. The tool rejected the device and told the
user *"Your SM_G935F is not yet supported by /e/ OS"*, which was not true: the
device was supported by the OS, just not matched by the installer.

Two things follow, and both belong in the proposal.

1. **A device fingerprint cannot be a string comparison against a hardcoded list.**
   Variants, regional SKUs and hardware revisions collide with naming. Building a
   representation that is rich enough to drive a verdict and robust to this is the
   substantive technical challenge, and this is the evidence for it.
2. **`cannot-verify` has to be a first-class verdict.** "This is probably that
   device but I cannot establish it" is a real and frequent condition. This tool had
   nowhere to put it, so the condition came out as a false negative wearing the
   wrong error message. Harmless here. The same missing state in the other direction
   is a brick.

---

## 5. postmarketOS

<https://docs.postmarketos.org/pmaports/main/device-categorization.html>

Maintains a categorised device support matrix with per-device state. Not a verifier,
and not a competitor. Relevant twice over: as an existing structured device dataset
whose categorisation scheme should inform the schema here rather than being
reinvented, and as an ecosystem partner for Q7.

---

## Where each of these belongs in the application

| Question | Use |
|---|---|
| Q1 outcomes | The verification-layer framing, and the two-corpus validation plan that OpenAndroidInstaller's configs make possible |
| Q5 comparison | OpenAndroidInstaller first, fwupd/LVFS second, then the flasher table |
| Q6 challenges | The /e/OS codename case, as concrete evidence for the fingerprint problem and the abstain verdict |
| Q7 ecosystem | OpenAndroidInstaller, postmarketOS, LineageOS as named communities, with the matrix and corpus formats published as reusable open data |
