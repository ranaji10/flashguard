# Flashguard

Flashguard checks whether a set of instructions for reinstalling an OS on a phone or
tablet (a **provisioning recipe**) is safe for one specific device, **before anyone runs
it**. You plug a device into a computer and a read-only kit reads its parameters (a
**fingerprint**): the USB description through a web browser, and the Android properties
through one terminal command. Flashguard compares that fingerprint with a recipe written from
the device configurations that public projects publish (LineageOS, OpenAndroidInstaller,
postmarketOS) and gives back one of four answers:

- **safe**: the recipe fits this device, and the device is ready for it.
- **not-ready**: the recipe fits this device, but the device is not ready yet, for example
  because its bootloader is still locked. The answer says what to do, and the device is
  checked again afterwards.
- **unsafe**: the recipe would harm this device, for example by leaving it unable to start.
- **cannot-verify**: there is not enough evidence to decide. This is a normal answer, not
  an error.

Flashguard never runs the recipe and never touches a device. It is a plain function: data
in, answer out.

**Why it matters.** Many phones and tablets still work but no longer get updates from their
maker. Community systems such as LineageOS and postmarketOS can give them a second life,
but one wrong step can permanently break ("brick") a device. Today, avoiding that depends on
rare expert knowledge of each model. Flashguard makes that check automatic and open, so
people, and the tools they build, can return old devices to use with less risk.

**The one rule.** A wrong "safe" is the only mistake that is never acceptable. When in
doubt, Flashguard answers cannot-verify.

Flashguard is the only thing this grant application funds. *RePurpose* is a working name for
wider ideas beyond it, which are out of scope here.

## For reviewers: start here

Read in this order.

1. `docs/reasoning/verdict-contract.md`: exactly what each of the four answers means.
   Written before the code; the code is tested against it.
2. `flashguard/verify.py`: the verifier itself.
3. `data/recipes/README.md`: the test recipes for real devices, listed in one table. Each
   one records the answer a person expects, so the verifier's answers can be checked.
4. `docs/reasoning/verdict-gap.md`: why the verifier sometimes says cannot-verify where a
   person would say unsafe.
5. `docs/reasoning/prior-art.md`: existing projects and how this one differs.
6. `bench-kit/`: the read-only kit volunteers use to collect device fingerprints. The
   results are in `data/device-matrix.jsonl`.
7. `grant/schedule.md`: the planned milestones, each with a test anyone can check from
   published files. `grant/nlnet-restack-proposal.md` is the working draft of the proposal.

For a map of every document, see `docs/INDEX.md`.

## Where things stand

- A working verifier (`flashguard/verify.py`) that reads recipe formats v0.1 to v0.3.
- Eighteen test recipes for twelve real phone models, in `data/recipes/` and
  `data/recipes-v0.2/`.
- Device fingerprints collected at volunteer test sessions, in `data/device-matrix.jsonl`.
- So far, no false "safe" answers. Most answers are still cannot-verify. That is expected
  at this stage: the verifier holds back whenever a device does not report what it needs,
  or when no phone of that model has been captured yet.
- One test recipe is expected to return `unsafe`, and does: an OpenAndroidInstaller
  configuration that calls the POCO F3 a single-layout phone, while the phone itself reports
  A/B slots. Six recent labels rest on public sources only, by choice (see
  `data/recipes/README.md`).

The numbers change as data comes in. To see the current ones, run `python3 data/coverage.py`.

### What the October test sessions showed

Fifteen volunteers have read 40 distinct Android phones, from a 2011 Sony Ericsson to
a 2025 Pixel. Three findings shape the verifier:

- **Bootloader lock state is readable on every phone running Android 8 or later** (24 of 24),
  and on only 3 of 16 older ones. What counts is the Android version the phone runs now, not
  the one it shipped with: a Galaxy S8 launched on Android 7 and updated to 9 reports it.
- **A/B storage layout is reported directly** by every phone that has it, and agrees with
  LineageOS each time the two can be compared. **No property ever reports a single
  layout.** Since 17 October the verifier reads a single layout from the absence of all three
  A/B markers, only on the maker's own release firmware (`docs/reasoning/layout-absence-rule.md`).
  On custom firmware it still answers cannot-verify.
- **Upstream data can be wrong, and the phone catches it.** One upstream configuration
  describes the POCO F3 as single-layout. The phone reports A/B, so the recipe built from that
  configuration is answered `unsafe`. This is why a layout the phone reports always wins over
  an inferred one.

Reading a phone is the weakest step. In one session, 13 of 37 attempts were retries where the
browser saw the phone but the terminal command could not reach it. The kit now warns the
tester before the terminal step when the browser read shows no debugging connection.

Only read-only work happens in this repository: detecting and describing devices (Tier A)
and checking recipes in simulation (Tier B). Running a recipe on real hardware (Tier C) is
not part of this work.

## Try it yourself

You need `bash` and Python 3. Node.js is optional (one extra check runs if it is present).
No device, network access or installation is needed.

```
git clone https://github.com/ranaji10/flashguard.git
cd flashguard
bash tests/all.sh          # every check that needs no device
python3 data/coverage.py   # current scoreboard: false safes, decided share, missing fields
```

`tests/all.sh` finishes with exit code 0 when everything passes. Lines saying
"BUILD MUST FAIL" during the run are self-tests: the suite plants a known mistake to prove
each check really catches it.

## What is in this repository

| Folder | What it holds |
|---|---|
| `flashguard/` | The verifier. `verify.py` is the main function. `reasons.py` and `guidance.py` turn its results into plain-language reasons and next steps. |
| `data/` | Open data. Device fingerprints (`device-matrix.jsonl`) and their format (`schema.md`), test recipes (`recipes/`, `recipes-v0.2/`), the word lists the verifier uses (`vocabulary.json`, `reason_codes.json`), volunteer results (`contributions/`), and scripts that merge and measure them (`merge.py`, `coverage.py`). |
| `tests/` | All automatic checks. `all.sh` runs them. Also sample device data used by the tests (`android/`, `fixtures/`, `real-descriptors/`). |
| `bench-kit/` | The read-only kit volunteers copy to a USB stick. Start at `START-HERE.html`. `STOP-LIST.txt` lists commands that must never be run. |
| `tools/` | Scripts for the people running the project: taking in volunteer results (`intake.py`), confirming device models (`confirm-model.py`, `model-sources.py`) and building the tester package (`build-package.sh`). |
| `docs/reasoning/` | Why the design is the way it is. |
| `docs/Research/` | Studies of the three main public sources of install instructions: LineageOS, OpenAndroidInstaller and postmarketOS. |
| `docs/reference/` | Procedures and records: the bench protocol, test runs, the consent text testers see. |
| `grant/` | The draft proposal and milestones. |

### Working files you can skip

These record how the work was done. They are kept for transparency but are not needed to
judge the idea.

- `docs/reference/producer-prompt-*.md`: task briefs given to an AI coding assistant (see
  "How AI was used" below).
- `docs/reference/review-log.md`, `docs/reference/review-workflow.md`,
  `docs/reference/handoff.md`, `docs/reference/sync-protocol.md`: how work was reviewed and
  passed between tools.
- `grant/work-log-2026-09-13.md`, `grant/nlnet-findings-2026-09-03.md`, `grant/_drafts/`:
  dated notes behind the proposal.
- `CLAUDE.md`, `.github/`, `.vscode/`, `project.code-workspace`: rules and settings for
  the AI assistants and the editor.
- `tests/handoff.sh`, `tests/review-*.sh`, `tests/tracker-export.py`,
  `tests/check-tracker.sh`, `tools/tracker.py`, `tools/derive-pending.py`: tools for the
  team's own workflow.

## Safety

- Nothing in this repository writes to a device. The bench kit only reads, and only from a
  fixed list of allowed properties.
- Personal identifiers are never recorded: serial number, IMEI, IMSI, MAC address, Android
  ID, ICCID or any account identifier. Checks enforce this
  (`tests/check-descriptor-privacy.sh`, `tests/check-public-safe.sh`).
- Commands that can wipe or brick a device are listed in `bench-kit/STOP-LIST.txt` and in
  `CLAUDE.md`, and are blocked for AI assistants by `.claude/settings.json`.
- Recipes are treated as untrusted input. They are checked against a schema before use and
  never passed to a shell.

## No machine learning

Flashguard contains none. The verifier is a fixed set of rules applied to a fingerprint and
a recipe. `bench-kit/scripts/classify.sh` is a fixed decision procedure over USB
information, and `classifier_confidence` is a number set by hand for each rule, not the
output of a model. Nothing here is trained, inferred or learned.

This is stated plainly because some of the words used could suggest otherwise, and because
NLnet's Restack programme excludes AI-related projects unless they already have more than a
million active users.

## How AI was used to build this project

Flashguard itself contains no AI. AI assistants were used as tools while building it:

- **Claude (Anthropic)**, in chat and agent sessions: background research, reading the
  public documentation of upstream projects, design reviews and audits, and writing
  detailed task briefs.
- **GitHub Copilot in VS Code**: day-to-day coding from those briefs. Research helpers
  defined in `.github/agents/` were only allowed to write into `docs/Research/`.
- **Reviews**: changes were checked by a second assistant that was not shown the first
  one's summary. Findings are logged in `docs/reference/review-log.md`.

How this was kept under control:

- A person made every design decision. Decisions are written down, for example in
  `docs/reasoning/rulings-2026-10-08.md`.
- Nothing counts as done until a test shows it. `tests/all.sh` runs before every commit.
- All assistants follow one written rulebook, `CLAUDE.md`. A test
  (`tests/check-rule-agreement.sh`) keeps the safety rules in Copilot's copy identical.
- Assistants are blocked from running commands that could harm a device
  (`.claude/settings.json`).

**Copyright and terms of use.** Under Anthropic's Consumer Terms (as read on 17 October
2026), Anthropic assigns to the user whatever rights it has in Claude's outputs, including
code, and makes no promise that outputs are original, accurate or free of others' rights.
The code Claude wrote here was written for this project from its own specifications and tests;
no file from another project was copied in, but a language model cannot prove that no line it
writes resembles existing code, which is one reason every change is reviewed and tested. The
code in this repository can be used freely under its licence (GPL-3.0-or-later), and the data
under CC0; that includes the parts an assistant wrote. In this project, third-party material (other projects' files, papers) is kept in a separate local
folder that is never committed. The scripts that study upstream projects count and classify
their files without copying their text into this repository (`data/survey_upstream.py`).
Test recipes are written independently from facts about each device, and each one records
where those facts came from (its `source` field). Anyone contributing with a code assistant is asked to follow the same
rule.

## For contributors

Turn on the pre-commit check once after cloning. It runs `tests/all.sh` before every
commit and stops the commit if something is broken.

```
git config core.hooksPath .githooks
```

Git cannot turn this on automatically. Without it, run `bash tests/all.sh` by hand.
To skip the check on purpose: `git commit --no-verify`.

## Licence

Code: **GPL-3.0-or-later** (`LICENSE`). Copyleft is deliberate: a safety checker whose
checks could be quietly weakened in a closed copy is worth less, and it keeps
OpenAndroidInstaller's GPL-licensed device files usable as a source of test recipes.

Data: **CC0-1.0** (`data/LICENSE`), covering the device fingerprints and test recipes, so
other reuse and repair projects can use them freely.
