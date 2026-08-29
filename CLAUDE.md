# Verifier. Repository context.

Given a **device fingerprint** and a **candidate provisioning recipe**, return
**safe / unsafe / cannot-verify** *without executing the recipe on hardware*.

Read `docs/verdict-contract.md` before touching verification logic. It is the
specification; the code is measured against it, not the other way round.

## Naming, which is a scope tool

**Flashguard** is the verifier: the one thing this grant funds. **RePurpose** is the working
title for the wider ambition beyond it. If a proposed feature belongs to RePurpose rather than
Flashguard, it is out of scope for this grant. Say so and stop.

Applicant: Ranaji Deb, sole applicant, in his own name.

## What is not built yet, and what that means for every session

As of 30 August 2026 the verifier **does not exist**. There is no
`verify(fingerprint, recipe)`, and `data/recipes/` holds no corpus. What exists is
a bench kit for collecting fingerprints, a device matrix, and a test suite for the
classifier — all of it instrumentation for producing the *inputs* to a function
nobody has written.

Two rules follow, and they bind an assistant more than they bind Ranaji, because
the bench kit is more immediately gratifying to improve and an assistant will drift
there by default:

1. **Do not extend the bench kit unless a tester is blocked.** It works. It produced
   a complete seven-field record on 29 August. Polishing it further is motion, not
   progress.
2. **When asked what to do next, the answer is the verifier** until one exists that
   runs against a corpus and reports a false-safe rate.

Delete this section when `verify()` exists and the gate runs.

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

## Facts about hardware are read, never recalled

Before stating any disk name, mount path, device model or machine name -- and
before writing any command that contains one -- read `docs/bench-hardware.md`.
Do not answer from the conversation, and do not answer from memory of an earlier
session. If the fact is not in that file, say it is not recorded and ask, rather
than supplying a plausible one.

This rule exists because a confidently wrong path or disk name inside `rm -rf`
or `cp -R` destroys a bench run, and because it has already happened once: an
earlier session repeated a stale USB stick name after being corrected.

If a hardware fact changes, update `docs/bench-hardware.md` in the same turn.

## Changes to the classifier are tested before they are believed

`bench-kit/scripts/classify.sh` is a pure function over `lsusb -v` text: no
device, no I/O, no side effects. Every change to it must be run against the
saved descriptors:

    bash tests/run.sh

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
