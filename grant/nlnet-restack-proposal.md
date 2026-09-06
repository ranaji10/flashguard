# NLnet / Restack (Open Internet Stack) — Proposal Working Document

> **Staging and iteration space, not the final submission.** The NLnet application is
> pasted into a web form, not uploaded. Draft here, paste the polished version when the
> call opens.

**Fund:** Restack (Open Internet Stack) · **Form:** <https://nlnet.nl/propose/>
**Call opens:** 3 September 2026 · **Deadline:** 3 November 2026, 12:00 CET
**Grant size:** €5,000 to €50,000, equity-free
**Project name:** **Flashguard** (the verifier, what this grant funds). *RePurpose* is the working
title for the wider ambition beyond the grant and is deliberately absent from this application.

---

## Changelog

| Date | Version | Change |
|---|---|---|
| 2026-08-26 | v0.1 | Initial skeleton, drafted problem statement |
| 2026-08-26 | v0.2 | Prior-art scan folded in. Q5 rebuilt around OpenAndroidInstaller and fwupd/LVFS. Two-corpus validation plan added to Q1 and Q4. Evaluation design and the false-safe metric added to Q1 and Q6. /e/OS codename case added to Q6. Data ethics added to Q7. Schedule split into `schedule.md`. |

Mark edited sections with `<!-- edited vNN -->` when revising.

---

## Scope guardrail. Read before editing anything.

**This proposal funds ONE thing: the recipe verifier.** Capability inference, path
generation, the repurposing platform, a marketplace, multiple scenarios: all explicitly
*future work*, not part of this grant. If a sentence starts describing a platform, cut it.
Over-scoping is NLnet's most common rejection reason.

---

## Verified against source, 26 August 2026

- Deadlines moved from even to odd months to avoid the summer break and FOSDEM. Calls
  resume 3 September 2026, first deadline 3 November 2026.
- Restack is one of three new programmes under Open Internet Stack, alongside
  **CodeSupply** and **ELFA**. **Read all three descriptions when the call opens before
  choosing where to submit.** Submitting to the wrong programme is a silent rejection.
- Restack funds an open internet stack across every layer from hardware through
  middleware to applications, with explicit interest in *"technical debt and things that
  were left intentionally broken."* €7M through 2030. All results must be released under a
  recognised free or open source licence.

Re-confirm before submitting. Figures move.

---

## The application, question by question

### Q1 — What are you going to make, and what are the expected outcomes?
*(Technical, specific, ~200 to 400 words. No marketing language.)* <!-- edited v02 -->

Millions of phones and tablets are discarded or left idle each year not because the
hardware has failed, but because the vendor stopped shipping software updates. Installing
community-maintained firmware can return these devices to safe, useful service. The
installation is the barrier. Flashing is model-specific, and a single wrong step — an
incompatible image, a mis-ordered command, a bootloader assumed unlockable that is not —
can permanently brick the device.

Tooling that *executes* provisioning is mature. OpenAndroidInstaller covers 88 devices,
LineageOS ships a browser installer, vendors ship their own flashers. Tooling that
*verifies* does not exist. None of these can answer, before anything runs, whether a
given recipe is safe for a given device, and none exposes that judgement as a component
other tools can call. Safety today rests on scarce per-model human expertise scattered
across forums and wikis. As recipes increasingly come from community contributors and
automated tooling, that does not scale, and the risk compounds.

This project builds the missing layer: an open, verifiable method with a reference
implementation that takes a device fingerprint and a candidate provisioning recipe and
returns **safe / unsafe / cannot-verify** *without executing the recipe on hardware*. It
combines static analysis of the recipe against the device's real partition and bootloader
state with a modelled flash state machine that detects sequences leaving a device
unbootable. Verification is a pure function with no device I/O, so the verifier
structurally cannot damage what it inspects.

Validation runs on two corpora, deliberately separated. **Recipe coverage**: hundreds of
real provisioning recipes drawn from published, openly licensed sources including
OpenAndroidInstaller's per-device configurations. **Device coverage**: tens of physically
fingerprinted devices from a volunteer tester network, contributing the read-only device
state only hardware can give.

Success is measured, not asserted. The primary metric is the **false-safe rate**: recipes
that would brick a device and were called safe. **The target is zero**, and it gates the
build. False-unsafe rate and abstention rate are reported alongside, so a verifier that
refuses everything cannot look successful. We publish the device-matrix and recipe-corpus
formats as open data so verdicts are reproducible and coverage is community-extensible.

The outcome is safety infrastructure for the right to reuse and repair. Automated
capability inference and safe-path generation, which would *consume* this verifier, are
named as future work and are not part of this grant.

*[TODO: tighten to the form's word limit once known.]*

---

### Q2 — Your relevant experience and contributions <!-- edited v04 -->

*Applicant: Ranaji Deb, sole applicant, in his own name. Drafted 26 Aug 2026 from the applicant's CV.*

**DRAFT v0.1:**

I am a product lead with more than ten years turning research-heavy, engineering-driven systems
into things people actually use. My foundation is technical rather than managerial.

**Technical foundation.** A B.Tech in Bioinformatics gave me statistics, probability, pattern
recognition and programming. My master's thesis at FAMU in Prague was in computer vision: I built
an algorithm that reads stock photographs and compares how a scene is understood by a human
against how it is understood by a machine. That thesis is the closest precedent for this proposal.
It was self-directed, built alone, and had to be defended on its method rather than its output,
which is exactly what a verification method has to survive.

**Building things that get finished.** At CloudChef I designed and shipped an automated inventory
forecasting tool that replaced manual planning outright, removing 21 hours of work a week. At
The/Nudge I defined and implemented the telemetry and KPI framework in Apache Superset that ran a
nationwide rollout, and owned the roadmap and backlog for a platform serving over 100,000
households. At Cognizant I led 18 enterprise software programmes from concept to go-live across
seven countries. The relevant fact in each is completion rather than scale.

**Proximity to the problem.** I currently lead product and European go-to-market for an agentic AI
company. The premise of this proposal, that provisioning recipes will increasingly be produced by
automated tooling rather than by a person who understands the device in front of them, is not
speculative to me. It is what I work on.

**Why device longevity.** My postgraduate work was in photography, with fifteen exhibitions across
Czechia, the USA and India and publication in five magazines. Equipment that outlives its vendor's
interest in it is a familiar problem rather than an abstract one.

**What I am not, stated deliberately.** I am not a firmware or Android systems engineer. That is
not an omission this project works around; it is the reason the project is shaped as it is. Safe
reuse today depends on scarce per-model expertise, and this design assumes an author who cannot
rely on having it: verification is a pure function that abstains by default, the device matrix and
recipe corpus are published so every verdict is reproducible by people who know more than I do,
and the primary metric is the false-safe rate rather than device coverage. A verifier built by
someone who has to earn each verdict from published evidence is the right tool for a problem
defined by expertise being scarce.

**Open source.** My public contribution record is thin, and the honest remedy is code rather than
claims: [REPO LINK] holds the read-only device fingerprinting, the recipe corpus and the verifier
reference implementation under GPL-3.0-or-later, with the device matrix under CC0.

---

**[YOU] before this is final:**

- [ ] Public repository URL. See `schedule.md`, milestone H1. Everything else in this answer is
      already true; this is the only sentence that is not yet.
- [ ] Make the existing private prototype repository public if nothing in its history embarrasses
      you. Two public repositories reads very differently from one.
- [ ] **Certified in Cybersecurity (ISC2) is listed as in progress on your CV.** Finishing it
      before submission is a genuine asset for a safety-tooling grant and belongs in this answer.
      If it will not be done by early October, leave it out rather than describing it as pending.
- [ ] Decide whether to name the employer in the agentic-AI paragraph or keep it generic. Naming is
      stronger; check nothing in your arrangement there objects to it.

### Q3 — Requested amount

**[YOU]** A number at or under €50,000. For a scoped verifier, reference implementation,
recipe corpus in the hundreds and a device matrix in the tens, €20k to €40k is plausible.
Break it down in Q4.

---

### Q4 — What will the budget fund? Other funding sources?

**[YOU]** Budget lines. Suggested shape:

- Your time in person-months, the large majority of the ask
- Corpus work: importing and normalising published recipe sources, deriving expected
  verdicts. This is real effort and it is what makes the validation claim defensible
- A small device-acquisition budget for gaps the tester network does not fill, targeted at
  chipset families and partition schemes rather than device count
- Tester-network costs: a handful of USB sticks, travel to two or three repair events

**Double-funding disclosure.** List any other grant applied for or held for the *same*
work. If other funding is pursued, it must be for *distinct* scope, stated clearly. The
same costs cannot appear in two grants.

---

### Q5 — Compare with existing or historical efforts <!-- edited v02 -->

**The claim, stated carefully.** Not that nobody verifies provisioning recipes. That is
too strong and a reviewer here will know it. The defensible claim is: **execution tooling
for community firmware is mature; verification tooling does not exist.**

**OpenAndroidInstaller** (<https://github.com/openandroidinstaller-dev/openandroidinstaller>)
is the closest existing project. GPL-3.0-or-later, actively maintained, per-device
configuration files covering 88 devices across Fairphone, Pixel, Motorola, OnePlus,
Samsung, Sony and Xiaomi. It is a real achievement and it is the tool this project is
built to serve. Its own README states the position precisely: *"use at your own risk!
While many people tested the application so far and we heard of no bricked devices, things
might still go wrong."* That is a report of accumulated experience, not a property of the
system. This project supplies the property. OpenAndroidInstaller executes; this verifies;
and its device configurations are one of our recipe-corpus sources.

**fwupd and the Linux Vendor Firmware Service** (<https://fwupd.org/>) are the reference
model for open firmware-update infrastructure and run a documented firmware testing
pipeline. Closest in spirit of anything that exists, and cited approvingly. Three
differences leave room: it covers PCs and peripherals rather than the Android provisioning
path; it verifies vendor-submitted firmware entering a trusted pipeline, whereas this must
judge an arbitrary recipe of unknown provenance against a specific device's current state;
and its safety model rests on vendor participation, which vendor-abandoned devices by
definition do not have.

**Browser and vendor flashers.** Google's Android Flash Tool executes, for Pixel devices
only. kdrag0n's fastboot.js is a WebUSB transport library and correctly makes no safety
claim. The LineageOS web installer executes, with safety supplied by per-device human
curation, which is exactly the scarce resource this project exists to stop depending on.
Heimdall, Odin and SP Flash Tool execute with no safety model at all.

**postmarketOS** maintains a categorised device support matrix. Not a verifier, and an
ecosystem partner rather than a comparator, but its categorisation scheme should inform
our schema instead of being reinvented.

Full scan with sources: `docs/reasoning/prior-art.md`.

---

### Q6 — Significant technical challenges you expect to solve <!-- edited v02 -->

**1. A device fingerprint robust enough to drive a verdict, obtainable read-only.**
Not a string comparison against a hardcoded list. The /e/OS Easy Installer detected a
Galaxy S7 edge correctly, then rejected it because the device reported its codename as
`hero2ltexx` while the supported list held `hero2lte`. A trailing regional suffix. The
user was told the OS did not support their phone, which was untrue. Variants, regional
SKUs and hardware revisions collide with naming, and this is the documented, reproducible
evidence for it.

**2. The abstain decision.** That same case shows why `cannot-verify` must be a
first-class verdict. "This is probably that device but I cannot establish it" is a
frequent, real condition. The /e/OS installer had nowhere to put it, so the condition came
out as a false negative wearing the wrong error message. Harmless in that direction. The
same missing state in the other direction is a brick. Our verdict contract makes
`cannot-verify` the default and requires unanimity for `safe`: one abstaining check
anywhere prevents a safe verdict.

**3. Modelling the flash state machine accurately enough to catch brick-causing
sequences without a real device.** Bootloader write ordering, A/B slot semantics,
verified-boot state transitions.

**4. Measuring this honestly.** The error types are not symmetric. A false *unsafe*
inconveniences someone. A false *cannot-verify* costs credibility. A false *safe* destroys
a device and the project's reason to exist. The false-safe rate is therefore the primary
metric with a target of zero, gating the build, and abstention rate is reported alongside
so caution cannot game it. Every misclassification becomes a permanent corpus case before
the rule that would catch it is written.

**5. Keeping matrix and corpus valid as ROMs and firmware revisions move.**

**Design property, not a challenge but worth stating.** Verification is a pure function:
fingerprint in, recipe in, verdict out, with no device I/O, no USB permission and no
network on the verify path. Anything touching hardware lives in a separate module the
verifier cannot call. "The verifier bricked my phone" is not a bug to prevent; it is a
sentence that cannot be true.

---

### Q7 — Ecosystem engagement and promoting the outcomes <!-- edited v02 -->

**Licensing.** Everything released under a recognised libre licence, as Restack requires.
GPL-3.0-or-later for code, which is also compatible with the OpenAndroidInstaller material
used as a corpus source. Device matrix and recipe corpus published as open data under
`[CC0 or CC-BY-SA-4.0, to decide]` so other reuse and repair projects can absorb them.

**Communities.** OpenAndroidInstaller as the most obvious first consumer of the verifier.
postmarketOS and LineageOS, whose published device data and install instructions are both
corpus sources and natural collaborators. Right-to-repair and e-waste networks.
**[YOU: name the specific forums and channels you can actually reach, and the Prague
repair and hackerspace groups by name.]**

**The tester network, and why it is research rather than crowdsourcing.** Volunteers run
a Tier A protocol that writes nothing to their devices. Every participant sees a
participation note before running anything: what is collected, what is published, under
what licence, and how to withdraw. An explicit exclusion list — serial numbers, IMEI,
IMSI, MAC addresses, Android IDs — is enforced in the collection scripts themselves, which
query an allowlist of properties rather than dumping device state, because the resulting
dataset is public. The protocol is piloted before it is fielded and the completion funnel
is measured, so we learn where non-specialists give up. That accessibility finding is
itself an outcome, and closer to what Restack funds than the device data alone.

**Reducing the barrier as a deliverable.** The recommended tester path is a bootable Linux
image with device rules preinstalled, which removes the Windows driver-installation step
that is the single largest source of volunteer drop-off. The Windows browser route is kept
and its friction logged, because smoothing it matters, but it is not the default first
experience.

**Publication.** The device-matrix and recipe-corpus formats are published as reusable
specifications, not just as data. Coverage is reported openly, including gaps.

---

## Open decisions before submitting

- [ ] Final project name. Flashguard is a placeholder.
- [ ] **Which of Restack / CodeSupply / ELFA.** Read all three on 3 September.
- [ ] Requested amount and person-month estimate.
- [ ] Applicant entity. Must be EU-anchored; a Prague address is fine for NLnet.
- [ ] Data licence: CC0 or CC-BY-SA-4.0.
- [ ] Public repository URL for Q1 and Q2. See `schedule.md`.
- [ ] Confirm exact form fields when the call opens.
