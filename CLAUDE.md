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
