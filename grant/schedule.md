# Milestones

*Rewritten 6 September 2026, from a calendar into a payment plan. NLnet pays on completion,
never upfront: "you divide your project into milestones... Once you reach a milestone you
send in a request for payment." A calendar cannot be invoiced.*

## The rule every milestone here has to satisfy

**Someone who is not on this project must be able to check it is done, from published
artefacts alone, without asking.** "Corpus built" is not checkable. "`data/recipes/` contains
40 recipes, each with a verdict and a stated reason, and `coverage.py` reports a false-safe
rate against them" is.

## Before the grant: what already exists

Not claimable, and not padding either. It is the evidence that the plan is real.

- Device matrix with 1 complete and 3 partial Android fingerprints, 8 physical devices.
- 9 real USB descriptors, `iSerial` stripped, 6 promoted to test fixtures with human ground
  truth.
- A 7-check test suite that runs with no device attached.
- Two classifier defects found, root-caused, fixed, and turned into regression tests.
- Read-only tooling with deny rules verified firing at two independent layers.

## M1 — Verifier and first corpus

**Done when:**

- `verify(fingerprint, recipe)` exists as a pure function matching
  `docs/reasoning/verdict-contract.md`: no device I/O, no network, no filesystem on the
  verify path.
- `data/recipes/` holds at least 10 recipes, 5 safe and 5 deliberately unsafe, each carrying
  the human reason for its verdict.
- `tests/all.sh` fails the build on a single false safe.
- `coverage.py` reports the false-safe count and the decided share as a pair, with
  `DECIDED_SHARE_FLOOR` set from the first real run.
- The ten-config hand-labelling experiment is written up, including if it failed.

**Checkable by:** cloning the repo and running `bash tests/all.sh`.

## M2 — Corpus at scale

**Done when:**

- At least 40 recipes derived from OpenAndroidInstaller device configs, LineageOS and
  postmarketOS install instructions, each with a verdict and a reason.
- Provenance and licence recorded per recipe. OpenAndroidInstaller's configs are GPL; where
  a recipe derives from one, that is stated.
- False-safe rate zero across the whole corpus, decided share at or above the floor.

**Checkable by:** the published corpus and the coverage output.

## M3 — Device matrix, with volunteers

**Done when:**

- 10 or more Android records carrying all seven verifier fields, across 3 or more chipset
  families, both partition schemes represented.
- Records from more than one tester, with descriptors returned and privacy-checked.
- The attrition log published: devices that could not be captured, and why.

**Checkable by:** `python3 data/coverage.py`, which prints this criterion as a scoreboard.

## M4 — Browser-side detection

**Done when:**

- A no-install browser path identifies and classifies a device, agreeing with the
  descriptors already captured.
- The limits are documented per platform, including where an install is unavoidable.
- `capture_route` distinguishes browser-obtained records from Linux-live ones in the matrix.

**Checkable by:** running it, and by the platform limits document.

**Depends on** the probe in `tests/webusb-probe.html`, which is half an hour and should
happen before this milestone is costed.

## M5 — Release and handover

**Done when:**

- Public repository, everything under a recognised open source licence in its entirety,
  written outcomes open access.
- Corpus and matrix published CC0.
- Documentation a stranger can follow without asking a question.
- At least one upstream project (OpenAndroidInstaller, LineageOS, postmarketOS) contacted,
  with the outcome recorded whatever it was.

## Costing

Deliberately not filled in yet, and the reason matters.

NLnet grants are almost entirely **time**. There is no infrastructure line here: the
verifier is a pure function, the console a static file, no server and no hosting bill. So
the budget is days per milestone times a rate, plus a small line for devices and travel to a
repair cafe or hackerspace.

Cost effectiveness is 30 percent of the score, and what is scored is whether the number is
**justified**, not whether it is low. A 32k ask with visible arithmetic beats a 50k round
number. Fill this in once M1 has actually been built, because the first milestone is the
only honest calibration for the rest.

| Milestone | Days | Rate | Amount |
|---|---|---|---|
| M1 Verifier and first corpus | | | |
| M2 Corpus at scale | | | |
| M3 Device matrix | | | |
| M4 Browser-side detection | | | |
| M5 Release and handover | | | |
| Devices and travel | | | |
| **Total** | | | |

*First proposals cap at 50 k€. Restack's 150 k€ per-proposal and 500 k€ lifetime ceilings
apply to later ones, so 50 k€ is not the programme maximum and should not be described as
one.*
