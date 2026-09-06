> ## Superseded in parts — read this first
>
> *Header added 6 September 2026.*
>
> Written **26 August 2026**, before either bench run, before the classifier existed, and
> before the NLnet open call was read. It sits in `reasoning/` because its method is still
> sound, but several of its conclusions have since been overtaken by contact with hardware
> and with the funder. **Do not quote a figure or a plan from this file without checking the
> replacement.**
>
> | What this file says | Now superseded by |
> |---|---|
> | Delivery assumes a Linux bench environment | `docs/reasoning/delivery-platform.md` — browser first, the bench kit is a means to an end |
> | The verifier is described as forthcoming, with no done criteria | `docs/reasoning/verifier-plan.md` — it still does not exist, and "done" is now defined |
> | False-safe rate as a single headline metric | `docs/reasoning/verifier-plan.md` — it is a **pair**; zero alone is trivially gameable by abstaining on everything |
> | Classifier design reasoned from first principles | `docs/reasoning/testing-protocol.md` and the two run logs — two defects were found only by contact with real devices |
> | Prior-art figures (88 devices, 523 stars, 380 issues) | Read on 26 August. **All of them move.** Re-confirm before quoting. |
> | Schedule as a calendar | `grant/schedule.md` — rewritten as milestones with payable criteria |
>
> What still holds: the tiering (A read-only, B simulation, C never before a grant
> decision), the abstain-under-uncertainty discipline, the pure-function shape, and the
> argument that a verifier which cannot say "I do not know" is worse than none.

# Verifier Readiness Review

> Assessment of the Repurpose folder and seven changes to strengthen the NLnet application.
Originally published as a private web page on 26 August 2026; kept here so the reasoning lives in the repository.

---

What is actually in the Repurpose folder, what it is worth to the build, and the seven changes most likely to strengthen the NLnet application before 3 November.

**Reviewed** 26 Aug 2026
**Scope** 6,747 files · 338 MB
**Deadline** 3 Nov 2026, 12:00 CET
**Changes made** none

### Bottom line

The project lives in two files totalling 12 KB. Everything else in the folder, all 338 MB of it, is downloaded material about building things with AI, and none of it mentions a phone, a bootloader, or a flash. It is a toolbox, not a knowledge base, so it does not want an index. It wants a one-page map and a hard wall between it and anything you publish.

The bigger finding is outside the folder. An open source project called OpenAndroidInstaller already ships per-device install configs for 88 devices under GPLv3, with an issue tracker full of the exact failures your verifier is meant to catch. That is your recipe corpus, your failure-mode catalogue, and the prior art your Q5 currently does not name.

## What is actually in the folder

Two documents are the project. `device-test-kit.md` defines the safety tiering, the device-matrix record schema and the tester protocol. `nlnet-restack-proposal.md` is the working draft of the grant application, correctly scoped to the verifier alone. Both are in good shape and the scope guardrail in the proposal is the single best thing in the folder.

The remaining 6,745 files are borrowed. I searched every markdown, Python, text and JSON file in `Resources/`, `FutureUse/` and `skills/` for any mention of fastboot, bootloader, firmware, flashing, WebUSB, LineageOS, postmarketOS or adb. Zero hits. The reference material and the project do not overlap at all on subject.

Downloaded skills repo 231 MB
Modal 56 MB
Autoresearch 45 MB
Other resources 6 MB
The project 12 KB

Most of that mass is not even content. It is 500-plus extracted video frames, a committed `.venv`, `__pycache__`, a `.git` directory from someone else's repository, and a `.pristine` folder that is a byte-for-byte duplicate of the token-saving demos sitting beside it. Excluding those, the real file count is 772, and the documents worth ever opening again number about ten.

One thing you can stop worrying about: the two `.env` files in `TokenSavingFrameworks` hold deliberately fake demo secrets (`sk_live_definitely_not_for_the_model`). Nothing real is exposed. The `.env.example` in the downloaded skills repo is placeholders only.

## On indexing: no, and here is what to do instead

Indexing pays off when a corpus is large, about your subject, and growing. This one is large, about a different subject, and static. Semantic search across generic AI-development tutorials returns generic AI-development advice, which any assistant already produces without retrieval. The retrieval value is close to zero, and the 96 percent of the folder that is video frames and virtual environments would actively dilute whatever signal remains.

The useful material is roughly ten named documents whose value is knowing *when* to open them. That is a routing decision, not a similarity search. Three cheap things do the job properly:

- **A root `CLAUDE.md`.** Any Claude Code session opened in this folder would then start with the project in view: what the verifier is, the tri-state verdict, the Tier A/B/C safety rule, and above all the scope guardrail from the proposal. That guardrail is the highest-value thing to automate, because over-scoping is what kills NLnet applications and an assistant with no context will happily help you over-scope.
- **A root `README.md` that is a map, not a catalogue.** Three lines on the project, the two files that are the project, and a "when you need X, open Y" table. Ten rows, not 772.
- **A wall between the project and the library.** The project should be its own directory that can become a public repository. The downloaded material must stay outside it permanently, for reasons in section 5.

There is one index genuinely worth building, and it is not of this folder. It is `device-matrix.jsonl`, which does not exist yet, plus a twenty-line script that reads it and prints coverage: how many devices, how many chipset families, how many A/B versus non-A/B, how many verifier runs matched expectation. That file is the project's actual database and its state of validation. Build that index and skip the other one.

## What the borrowed material is genuinely worth

An honest pass. Judged on whether it changes anything you would otherwise do, not on whether it is interesting.

| Resource | Verdict | Why |
| --- | --- | --- |
| Security For Vibe-Coded Apps | Use | The moment testers submit device records to an endpoint you are running a backend that accepts untrusted input from strangers. Its five items (env vars, row-level security, server-side validation, package hygiene, auth middleware) are exactly the surface you will expose. Read it the week you build submission, not after. |
| autoresearch diagrams skill | Use | Ignore the diagrams. The *pattern* is the point: generate, evaluate against fixed criteria, keep or discard, mutate, log to JSONL. Your test kit already says "every misclassification or missed catch, add a case, refine a rule, re-run." That is the same loop, unnamed. Borrow its structure and its append-only results log for the verifier's own rule set. |
| Token-saving frameworks | Use | Relevant because this is a solo build over months on a budget. The ones that matter here are the compressed `CLAUDE.md`, `permissions.deny` for noise, and plan-at-high / execute-at-medium. The other twelve are demo theatre for a video shoot. Skim the README table, take three, ignore the folders. |
| Modal deployment template | Later | A plausible way to host the device-matrix submission endpoint with bearer auth and no ops burden, if and when you need one. Not now, and the committed `.venv` should never travel with it. |
| Skills and routines references | Later | Genuinely useful for one narrow thing: packaging the Tier A/B tester protocol as a skill so a tester's own assistant walks them through it consistently. Also a scheduled check for the call opening on 3 September. |
| Website design prompts (548 KB) | Skip | A landing page is precisely the kind of thing the proposal's own scope guardrail tells you to cut. NLnet funds the verifier. Revisit after the grant decision, if ever. |
| Expo to App Store guide | Skip | Wrong form factor entirely. The phone is the target, not the host, and iOS cannot do any of this. The host is a desktop browser with WebUSB. |
| Downloaded skills repo (231 MB) | Skip | Someone else's lead-generation and content agency workspace. Nothing in it touches your subject, and section 5 explains why it is a liability rather than a neutral. |

## Seven changes that would strengthen the build

Ranked by how much each one moves the application. The first two came out of the prior-art scan and are the reason this review is worth reading.

1

### Name OpenAndroidInstaller, and position against it rather than around it

Your Q5 names Android Flash Tool, fastboot.js and the LineageOS web installer. It does not name [OpenAndroidInstaller](https://github.com/openandroidinstaller-dev/openandroidinstaller), which is the closest existing project by some distance: an actively maintained GPLv3 desktop installer covering 88 devices, with per-device configuration files, 523 stars and 380 open issues. A reviewer in this space will know it. Omitting it reads as either an incomplete scan or an avoided comparison, and both are costly.

Positioned correctly it helps you rather than threatens you. It *executes*. You *verify*. Its README says "use at your own risk" and "we heard of no bricked devices," which is a statement of hope, not a safety property. The honest framing of your project is the missing verification layer beneath tools that already execute, and OpenAndroidInstaller becomes your first consumer and your best Q7 ecosystem answer.

**Do**Rewrite Q5 around a claim that survives scrutiny: execution tooling is mature and verification tooling does not exist. Add [fwupd and LVFS](https://fwupd.org/) as the second comparator, since they are the reference model for open firmware update infrastructure and LVFS already runs a firmware testing pipeline, but for a different device class.

2

### Your corpus problem is already solved, and it is not made of phones

This is the weakest point in the current plan. Your seed table lists seven devices of which exactly one, the unknown Android, is a live positive case. Six are correct-negatives: an iPhone, a Kobo, two Fuji cameras, USB storage. A verifier validated on one live Android is not validated, and the budget line of "10 to 20 devices" makes the grant's deliverable hostage to how many phones you and your friends can physically obtain by a given date.

Recipes are not devices. OpenAndroidInstaller's 88 per-device configs are published, structured and GPL-licensed. postmarketOS maintains a categorised device support matrix. LineageOS publishes per-device install instructions for hundreds of models. You can run the verifier against hundreds of real recipes on day one, and reserve physical hardware for the thing only hardware can give you, which is the read-only fingerprint at Tier A.

**Do**Split the validation claim in two. Recipe coverage in the hundreds, drawn from published corpora. Device coverage in the tens, from the tester network. State both numbers in Q1. It transforms the deliverable from "validated on the phones I could find" into something with a defensible denominator.

3

### The proposal never says how you will know it works

You evaluate programmes for a living and the proposal contains no evaluation design. The test kit defines a recipe corpus with expected verdicts, which is the raw material for a measurement, but no metric is ever named and no target is set. Q6 gestures at the abstain decision without saying what would count as getting it right.

For a safety tool the error types are not symmetric, and saying so out loud is the sharpest thing you can put in this application. A false *unsafe* costs a person some inconvenience. A false *cannot-verify* costs a little credibility. A false *safe* destroys a device and the project's reason to exist. That asymmetry should be the stated design principle, with abstention as the default under uncertainty.

**Do**Add three lines to Q1: false-safe rate is the primary metric, the target on the published corpus is zero, and abstention rate is reported alongside it so a verifier that refuses everything cannot look successful. That is a measurable deliverable, and it is the part of this application nobody else applying could write as well as you.

4

### Fingerprint matching is the hard research problem, and there is a citable case for it

The /e/OS Easy Installer detected a Galaxy S7 edge correctly, then rejected it because the device reported its codename as `hero2ltexx` while the supported list held `hero2lte`. A trailing regional suffix. The user was told their phone was unsupported by the operating system, which was not true.

That failure went the harmless direction, but it is the perfect illustration of your Q6 challenge: a device fingerprint rich enough to drive a verdict cannot be a string comparison against a hardcoded list, because variants, regional SKUs and revisions collide with the naming. It is also a clean argument for why *cannot-verify* has to be a first-class verdict rather than a failure state, since "this is probably that device but I cannot establish it" is a real and frequent condition.

**Do**Use it as a worked example in Q6. A named, documented, reproducible failure from a shipping tool beats an abstract description of the difficulty, and it shows you scanned the space rather than imagining it.

5

### The device matrix is primary data collection and is not yet treated as such

You are asking volunteers to run a tool on their hardware and submit structured records that will be published as open data. You write IRB materials as part of your day job, and none of that discipline has been applied here yet. Three gaps, all cheap to close.

- **An explicit exclusion list in the schema.** Serial numbers, IMEI, IMSI, MAC addresses and Android ID must never be recorded. The current schema reads `ro.product.*` properties, which is safe, but a helpful tester pasting a full `getprop` dump into `notes` would leak identifiers straight into a public dataset. Say so in the schema itself, where it will actually be read.
- **A short participation note.** What is collected, what is published, under what licence, how to withdraw a record.
- **A licence on the matrix and corpus.** NLnet requires libre release. Decide now whether the data is CC0 or CC BY-SA, because it determines whether other projects can absorb it, which is your Q7 argument.

**Do**Add the exclusion list to the schema, and a participation paragraph to the test kit. If Tier C ever happens, it needs a real written consent instrument, not a logged verbal yes.

6

### The Windows driver step will cost you most of your testers

Step 2 of the tester protocol asks people to install a WinUSB driver with Zadig before fastboot devices become visible. You have flagged it honestly as friction worth logging. In practice it is where a volunteer with a spare hour decides this is not their evening, and it is doubly unfortunate because driver-swapping *feels* dangerous even though Tier A writes nothing.

A bootable Linux image with the udev rules already in place removes the problem entirely rather than documenting it. It also does something rhetorically useful: the 2012 Acer in your seed table becomes a machine whose vendor support ended in October 2025, running the tool that returns other abandoned devices to service. The project demonstrates its own thesis in its test rig.

**Do**Make the live image the recommended tester path and the Windows browser route the fallback. Keep logging the Windows friction, because smoothing it is a legitimate deliverable, but stop making it the default first experience.

7

### Ten weeks, no schedule

The call opens 3 September and closes 3 November at noon. Neither document contains a date other than the deadline, and Q2 asks for a repository link that does not yet exist. Solo applications fail here more often than on substance: the proposal is fine and the evidence it promises to cite was never produced in time.

**Do**Work backwards from 3 November and fix three dates: public repository with the read-only Tier A spike, first N matrix records from real testers, and all seven answers drafted with a week of margin. Put them in the proposal document, where you will see them.

## Checked against the source

**Your grant dates are correct.** NLnet paused open calls in June 2026 to take stock of a decade of Next Generation Internet work, and moved deadlines from even to odd months to avoid the summer break and FOSDEM. Calls resume 3 September 2026 with the first deadline on 3 November. Restack is one of three new programmes under the Open Internet Stack umbrella, alongside CodeSupply and ELFA.

**Restack's scope fits, and is worth reading against your framing.** It funds an open internet stack across every layer from hardware through middleware to applications, with an explicit interest in "technical debt and things that were left intentionally broken." Abandoned-by-vendor devices are close to a literal instance of that phrase, and it is worth borrowing. Grants run €5,000 to €50,000 with €7 million allocated through 2030, and all results must be released under a recognised free or open source licence.

**The licensing hazard is real and it is in this folder.** That last requirement is why the wall in section 2 matters. The folder currently holds material from a paid course, a third-party GPL-adjacent workspace with its own git history, and assorted downloaded skills of unclear provenance. None of it can enter a repository you release under a libre licence, and the 231 MB directory is the kind of thing that ends up committed by accident during a late-night push. Keep the project in a directory that has never contained any of it.

**One open question worth ten minutes.** Restack is described as still being set up. Three sibling programmes now exist where one call used to be, and CodeSupply in particular may target something closer to your work. When the call opens on 3 September, read all three descriptions before choosing where to submit. Submitting to the wrong programme is a silent rejection.

## Sources

- [NLnet changes deadlines to odd months](https://nlnet.nl/news/2026/20260803-phaseshift.html)
- [Transitioning from NGI to Open Internet Stack, open calls temporarily paused](https://nlnet.nl/news/2026/20260612-NGIZero-stocktaking.html)
- [NLnet Restack programme](https://nlnet.nl/restack/)
- [OpenAndroidInstaller on GitHub](https://github.com/openandroidinstaller-dev/openandroidinstaller)
- [Easy installer incorrectly reports /e/OS compatibility, /e/OS community](https://community.e.foundation/t/easy-installer-incorrectly-reports-e-os-compatibility/42475)
- [LVFS, Linux Vendor Firmware Service](https://fwupd.org/)
- [postmarketOS device categorization](https://docs.postmarketos.org/pmaports/main/device-categorization.html)
- Local: `device-test-kit.md` and `nlnet-restack-proposal.md` in the Repurpose folder, plus a full inventory of `Resources/`, `FutureUse/` and `skills/`.
