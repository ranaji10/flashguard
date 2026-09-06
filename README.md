# Verifier for safe device provisioning

**Flashguard** — the verifier, and the only thing the grant funds.
*RePurpose* is the working title for the wider ambition beyond this grant, and is out of scope here.

## No machine learning

Flashguard contains none. The verifier is a pure function over a device fingerprint and a
provisioning recipe. `bench-kit/scripts/classify.sh` is a deterministic decision procedure
over USB descriptor fields, and `classifier_confidence` is a constant assigned by hand to
each rule, not a model output. Nothing here is trained, inferred or learned.

This is said plainly because the vocabulary invites the wrong reading, and because NLnet's
Restack programme places AI-related projects out of scope unless they already have more
than a million active human users.

Given a **device fingerprint** and a **candidate provisioning recipe**, this returns
**safe / unsafe / cannot-verify** without executing the recipe on hardware. It combines
static analysis of the recipe against the device's real partition and bootloader state
with a modelled flash state machine that detects command sequences leaving a device
unbootable.

It does not flash anything. It verifies what something else proposes to flash.

## Status

Pre-prototype. Tier A (detect and fingerprint, read-only) and Tier B (verify in
simulation) only. No hardware is written to by anything in this repository.

## Layout

    docs/
      device-test-kit.md      Tier A/B protocol and the tester-facing procedure
      verdict-contract.md     What safe / unsafe / cannot-verify mean. Written first.
      prior-art.md            What already exists and how this differs
      participation-note.md   Shown to testers before they run anything
    grant/
      nlnet-restack-proposal.md
      schedule.md
    data/
      schema.md               Record schema, including the exclusion list
      device-matrix.jsonl     Collected records
      recipes/                Golden corpus, each with an expected verdict
    bench-kit/                Copy to a USB stick, carry to the bench machine
    .claude/settings.json     Deny rules that make destructive commands unreachable

## Licence

Code: **GPL-3.0-or-later** (`LICENSE`). Copyleft is deliberate. A safety verifier whose
checks can be quietly weakened in a closed fork is worth less as safety infrastructure,
and it keeps OpenAndroidInstaller's GPL-licensed device configs usable as a corpus source.

Data: **CC0-1.0** (`data/LICENSE`), covering the device matrix and recipe corpus, so other
reuse and repair projects can absorb the records with no friction at all.
