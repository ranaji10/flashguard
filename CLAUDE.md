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
