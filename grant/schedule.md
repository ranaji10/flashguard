# Milestones

*Rewritten 11 October 2026 from the state of the repository on that day. The first version
(6 September) planned work that has since been done; that work now sits under "Before the
grant", and the milestones below are what the grant would fund. NLnet pays on completion,
never upfront: "you divide your project into milestones... Once you reach a milestone you
send in a request for payment."*

**The targets below are proposals for Ranaji to set.** Each number is a suggestion sized
from what one person has done in six weeks, not a commitment.

## The rule every milestone here has to satisfy

**Someone who is not on this project must be able to check it is done, from published
artefacts alone, without asking.** "Corpus built" is not checkable. "The corpus holds at
least 60 recipes, each with two labels and a written reason, and `coverage.py` reports the
false-safe count against them" is.

## Before the grant: what already exists

Not claimable, and not padding either. It is the evidence that the plan is real. Figures are
as of 11 October 2026; run `python3 data/coverage.py` for today's.

- **A working verifier**, `flashguard/verify.py`: a pure function, no device I/O, returning
  one of four verdicts (safe, not-ready, unsafe, cannot-verify), each with plain-language
  reasons, the evidence it used, and the scope of what it did not check
  (`docs/reasoning/verdict-contract.md`). It checks identity against public model sources
  and each operation's preconditions against the phone's reported state. It does not yet
  model the order of operations.
- **A test corpus of 15 recipes for 10 phone models**, in three format versions, each with a
  human assessment, an expected verdict and a written reason, and the source its facts came
  from (`data/recipes/README.md`).
- **Measurement that cannot be gamed by refusing.** The build fails on a single false safe;
  the decided share is reported beside it against a floor that may only rise
  (`data/coverage-floor.json`, 20%). As of 11 October: 0 false safes across 24 runs, decided
  on 2 of 7 distinct phone-and-recipe pairings, and the information lost between a human
  reading and the recipe format reported per format.
- **A device matrix of 37 records, 26 of them Android, from 8 testers**, captured through
  three routes (adb on a host, a live Linux stick, and a browser). 5 distinct phones carry
  all seven verifier fields; 6 more carry every field their storage layout reports.
- **A read-only tester kit**: a browser console for macOS, Windows and Linux
  (`bench-kit/START-HERE.html`), allowlisted capture scripts, a participation note and
  consent text, an intake tool that refuses personal identifiers, and two field rounds
  (a hackerspace evening in September, LinuxDays Prague in October).
- **Upstream research**: LineageOS (737 device pages), OpenAndroidInstaller (90 configs) and
  postmarketOS (668 device packages) studied and compared (`docs/Research/`). Questions put
  to OpenAndroidInstaller and LineageOS; LineageOS has answered.
- **A test suite that runs before every commit with no device attached** (`tests/all.sh`),
  and a claims registry (`data/claims.json`) that fails the build if the proposal quotes a
  number the data does not support.

**Known gaps, stated so the milestones can be read against them:**

- Most phones do not report their storage layout, so the verifier abstains on them. A
  further testing round to close this gap for A/B phones is under way before submission.
- No recipe in the corpus is expected to return `unsafe` yet.
- Labels have one author. Three recent labels rest on public sources only, deliberately,
  because nobody on the project owns those phones.
- The order of flashing steps is not modelled.

## M1. Corpus at scale, labelled independently

**Done when:**

- The corpus holds at least 60 recipes drawn from OpenAndroidInstaller, LineageOS and
  postmarketOS, each citing its source at a pinned commit, with both labels and a written
  reason.
- At least 10 of them are expected to return `unsafe` for a documented reason (wrong model
  sharing a codename, wrong storage layout, a step that needs an unlock the phone reports
  as locked).
- Every label has been checked by a second person, from the cited source only, before it
  counts toward a reported figure. Disagreements and how they were settled are published.
- A labelling-consistency test is written up: ten upstream configurations labelled
  independently by two people, with their agreement reported, including if it is poor.

**Checkable by:** the published corpus, the review record, and `python3 data/coverage.py`.

## M2. Verifier 1.0

**Done when:**

- The order of operations is modelled for the sequences the corpus contains (for example
  a write before the unlock it needs, or a slot switch on a phone without slots), and each
  rule has a corpus case that fails without it.
- The recipe format and reason codes are versioned and published as a JSON schema, with a
  stated policy for changing them.
- Across the whole corpus: false safes remain zero, and the decided share meets a floor
  raised from today's 20% to a figure set from M1's results.
- Every abstention is reported by kind, so a reader can see how many are the phone being
  silent and how many are gaps this project can still close.

**Checkable by:** cloning the repository and running `bash tests/all.sh` and
`python3 data/coverage.py`.

## M3. Device matrix across storage layouts

**Done when:**

- At least 30 distinct phones are complete for their storage layout, across at least
  8 chipset families, from more than 10 testers.
- Both A/B and single-layout phones are represented with positive evidence of their layout,
  so the verifier can decide on single-layout phones rather than abstaining on all of them.
- Capture is documented per platform and route (browser, adb, live Linux), including where
  an installation is unavoidable, and the attrition log of devices that could not be
  captured is published.

**Checkable by:** `python3 data/coverage.py`, which prints this as a scoreboard, and the
published platform notes.

## M4. A component other tools can call

**Done when:**

- The verifier can be called without reading its source: a documented command-line entry
  point and Python interface that take a fingerprint and a recipe as JSON and return the
  verdict object.
- Recipes can be generated from at least one upstream format (OpenAndroidInstaller
  configurations) by a published converter, so other projects can check their own
  procedures.
- The interface is offered to at least one upstream project, with the outcome recorded
  whatever it is.

**Checkable by:** the documentation, the converter's tests, and the recorded exchange.

## M5. Release and handover

**Done when:**

- A tagged release, everything under a recognised open source licence in its entirety,
  written outcomes open access.
- Corpus and matrix published under CC0.
- Documentation a stranger can follow without asking a question.

**Checkable by:** the release page and the repository.

## Costing

Deliberately not filled in yet.

NLnet grants are almost entirely **time**. There is no infrastructure line here: the
verifier is a pure function, the console a static file, no server and no hosting bill. So
the budget is days per milestone times a rate, plus a small line for devices and travel to a
repair cafe or hackerspace.

Cost effectiveness is 30 percent of the score, and what is scored is whether the number is
**justified**, not whether it is low. The six weeks already spent are the best calibration
available for the days below.

| Milestone | Days | Rate | Amount |
|---|---|---|---|
| M1 Corpus at scale, labelled independently | | | |
| M2 Verifier 1.0 | | | |
| M3 Device matrix across storage layouts | | | |
| M4 A component other tools can call | | | |
| M5 Release and handover | | | |
| Devices and travel | | | |
| **Total** | | | |

*First proposals cap at 50 k€. Restack's 150 k€ per-proposal and 500 k€ lifetime ceilings
apply to later ones, so 50 k€ is not the programme maximum and should not be described as
one.*
