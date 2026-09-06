# Verifier. Repository context.

Given a **device fingerprint** and a **candidate provisioning recipe**, return
**safe / unsafe / cannot-verify** *without executing the recipe on hardware*.

Read `docs/reasoning/verdict-contract.md` before touching verification logic. It is the
specification; the code is measured against it, not the other way round.

## Naming, which is a scope tool

**Flashguard** is the verifier: the one thing this grant funds. **RePurpose** is the working
title for the wider ambition beyond it. If a proposed feature belongs to RePurpose rather than
Flashguard, it is out of scope for this grant. Say so and stop.

Applicant: Ranaji Deb, sole applicant, in his own name.

## Current state

The v0.1 pure verifier exists at `flashguard/verify.py`, and five independently
authored corpus recipes exist under `data/recipes/`. The corpus replay reports five
`cannot-verify` results, zero decided results, and zero false safes. V0.1 has no
defensible `safe` case; see `docs/reasoning/safe-case.md`.

The bench kit remains frozen unless a tester is blocked. It produced a complete
seven-field record on 29 August; further polishing is out of scope while the
verifier's corpus and safety contract are being settled.

## Scope guardrail

This repository is **one thing: the recipe verifier.** Capability inference, path
generation, a platform, a marketplace, an app, a website: future work, out of scope,
do not add. Over-scoping is the most common reason NLnet rejects a proposal, and it
is the most expensive kind of help an assistant can offer here.

## Non-negotiable design properties

1. **Verification is a pure function.** Fingerprint in, recipe in, verdict out.
   No device I/O, no USB permission, no network on the verify path. Anything that
   touches hardware lives in a separate module that the verifier cannot call.
2. **False-safe is the only unacceptable error.** Build fails if the golden corpus
   produces a single one. `false_unsafe` and `abstain_rate` are tracked, not gated.
3. **cannot-verify is a first-class verdict.** Abstain under uncertainty. A verifier
   that refuses everything is a failure too, which is why abstain rate is always
   reported alongside.
4. **Recipes are untrusted input.** Schema-validate before parsing. Never
   interpolate a recipe field into a shell or an eval.

## Two assistants, one rulebook

This repository is worked on from two places: Claude sessions (research, audits, sweeps,
anything needing the web) and VS Code with Copilot (day-to-day code). Copilot does not read
this file. It reads `.github/copilot-instructions.md`, which is an ABRIDGED version of the
rules here.

**Nothing is done until a command proves it.** Write the failing check before the
implementation, run it, show it failing. End work with the command that proves it and its
output. Describe what exists in the present tense and what does not in the conditional —
a run log that claimed to cover work it predated cost this project a week, and it read
perfectly well.

**Hand off with a commit, never with prose.** Run `bash tests/handoff.sh` and paste its
output into the receiving session. "I fixed the classifier" is unverifiable and invites the
other side to build on a belief; a SHA cannot be misremembered. Full protocol in
`docs/reference/handoff.md`.

**This file stays the source of truth.** When a rule changes here, change it there too, and
keep that file short: repeated and verbose instructions crowd out the code being reviewed and
make Copilot worse, not better.

## Every document is indexed, and the index is enforced

`docs/INDEX.md` maps each decision to the file that holds it. `tests/check-index.sh` fails
the build when a path named in the index or in OPEN.md does not exist, and when a file under
`docs/` is not listed in the index. A new document must be indexed or the suite fails.

This exists because on 6 September an audit found eleven decisions written into no file at
all, and three files claiming to cover work they predated. The tracker said the second bench
run was written up; the write-up did not exist. Nothing checked, so nothing caught it.

**When a decision is made in conversation, it is not made until it is in a file.** Write it
where it will be read, add it to the index, and run `bash tests/all.sh`.

`docs/` is split: `reasoning/` for why things are the way they are, read before changing a
design or writing the proposal; `reference/` for facts and procedures you look up, with
`reference/runs/` for dated logs.

## No machine learning, and no vocabulary that suggests otherwise

Flashguard contains no model, no training and no inference. `classify.sh` is a deterministic
decision procedure over USB descriptor fields; `classifier_confidence` is a hand-assigned
constant per rule. Never describe any part of this project in ML or AI terms, never add a
component that would need them, and keep the plain statement in `README.md` intact.

NLnet Restack places AI-related projects out of scope unless they already have over a
million active human users. The exclusion is not a risk to the design. It is a risk to how
the design reads.

## Facts about hardware are read, never recalled

Before stating any disk name, mount path, device model or machine name -- and
before writing any command that contains one -- read `docs/reference/bench-hardware.md`.
Do not answer from the conversation, and do not answer from memory of an earlier
session. If the fact is not in that file, say it is not recorded and ask, rather
than supplying a plausible one.

This rule exists because a confidently wrong path or disk name inside `rm -rf`
or `cp -R` destroys a bench run, and because it has already happened once: an
earlier session repeated a stale USB stick name after being corrected.

If a hardware fact changes, update `docs/reference/bench-hardware.md` in the same turn.

## Changes to the classifier are tested before they are believed

`bench-kit/scripts/classify.sh` is a pure function over `lsusb -v` text: no
device, no I/O, no side effects. Every change to it must be run against the
saved descriptors:

    bash tests/all.sh

The kit targets **bash 3.2**, because macOS still ships it. No `declare -A`, no
`mapfile`, no `${v,,}`. `tests/check-portability.sh` enforces this; `bash -n` does
not, because these fail at runtime rather than at parse. Code written and tested
only on Linux has already broken this way once.

A failing fixture is fixed in `classify.sh`, not by editing the fixture --
unless the fixture's expected class was itself wrong, which must be recorded in
a `#!note` line explaining why. Adding a device class or a vendor to a list
means adding a fixture in the same commit.

Both classifier defects found on the first bench run were latent in data that
had already been collected and thrown away. Descriptors are now saved on every
capture, with `iSerial` stripped, so no evidence is discarded again.

## Guardrails: verified 26 August 2026

Two independent layers, both tested rather than assumed.

**Layer 1, this file.** The model reads the never-run list and the safety tiering and refuses.
Tested twice. It declined `fastboot flash boot test.img` citing the tiering, and it also declined
`adb root`, which is NOT on the never-run list, reasoning from the design properties instead. The
documentation layer over-covers, which is the right direction to err.

**Layer 2, `.claude/settings.json`.** Mechanical, fires regardless of phrasing. Tested with an
inert command chosen because nothing about it is device-related:

    dd if=/dev/null of=/dev/null count=0
    -> Permission to use Bash with command dd if=/dev/null of=/dev/null count=0 has been denied.

It matched on the command pattern without evaluating that `count=0` makes it a no-op. That is
correct for a backstop: pattern-level blocking, not semantic judgement.

Syntax note: `Bash(cmd:*)` and `Bash(cmd *)` are equivalent trailing wildcards. Compound commands
are parsed, so a deny rule still catches `cd /tmp && fastboot erase userdata`, and deny matches
past leading environment assignments.

**Known gap, which is why the printed stop list still matters.** Deny rules inspect the command
Claude types, not what that command then reads. `bash script.sh` is matched as `bash script.sh`;
a destructive line *inside* the script is invisible to the permission layer. The same applies to
environment runners such as `docker exec` and `npx`, which are not unwrapped. Since this project
runs its own tooling as `bash 01-detect.sh`, that gap is live: review what a script contains
before running it, and keep `bench-kit/STOP-LIST.txt` on the wall.

## Never run these

    fastboot flashing unlock      fastboot oem unlock
    fastboot flash ...            fastboot erase ...
    fastboot format ...           fastboot update ...
    fastboot set_active ...       adb disable-verity
    dd ...

`.claude/settings.json` denies them. Verify the deny rules actually match before
relying on them: ask for `fastboot flash boot test.img` and confirm the refusal.

## Data rules

`data/device-matrix.jsonl` is published as open data. Never record, in any field
including notes: serial number, IMEI, IMSI, MAC address, Android ID, ICCID, account
identifiers. `bench-kit/scripts/` query an explicit property allowlist for this
reason. Do not replace them with a `getprop` dump.

Raw command output goes in `raw/`, which is gitignored, and is deleted once the
scrubbed record is written.
