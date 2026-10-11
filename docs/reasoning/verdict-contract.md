# Verdict contract

**Status: specification. Written before implementation, deliberately. The code is
measured against this document, not the other way round.**

Version 0.3. First written 13 September 2026; updated 24 September (the `not-ready` verdict)
and 8 October 2026 (models settled from public sources, pending confirmation). Checked
against `flashguard/verify.py` on 11 October 2026.

---

## What the verifier is asked

    verify(fingerprint, recipe) -> { verdict, reasons[], coverage, evidence, scope }

`pending_confirmation: true` is added when the verdict is `not-ready` only because a person
has to confirm the model (see `not-ready` below).

`fingerprint` is what is known about one specific device, field by field, each field
carrying its provenance and whether it was actually observed.

`recipe` is an ordered sequence of provisioning operations plus references to the
assets they write or prerequisites they declare.

`verdict` is one of four values: `safe`, `not-ready`, `unsafe`, `cannot-verify`. There is
no fifth value and no numeric score in the output. A score invites a person to set their own threshold,
which relocates the safety decision to the least informed point in the system.

---

## The four verdicts

Ruled 24 September 2026: `unsafe` was being used for two different situations, a recipe
that does not fit the phone and a phone that is not ready for a recipe that does. They
are now separate verdicts. Neither is `safe`, so the false-safe gate is unchanged.

### `unsafe`

At least one condition has been **identified** under which executing this recipe on
this device would leave it unbootable or unrecoverable, or the recipe contains an
operation whose preconditions are provably unmet by this fingerprint.

Examples: an image built for a different model; a bootloader written
before the sequence can complete; a slot assumption contradicted by the device's
actual partition scheme; an operation requiring an unlocked bootloader on a device
reporting locked.

`unsafe` is a positive finding. It requires evidence, not absence of evidence.

### `not-ready`

The recipe fits this phone (codename, model and storage layout all confirmed), and the
phone is not yet in the state the recipe needs: the bootloader is still locked, or it runs
a different Android version. Each unmet condition is a reason with `result: "unmet"` and a
plain `remedy` (for example: unlock the bootloader, which erases the phone, then read the
phone again).

`not-ready` requires confirmed identity. If any identity check abstained, the recipe might
not fit this phone at all, so the verdict is `cannot-verify` and the unmet reason stays in
the list. A remedy is guidance, never evidence: after following it, the phone is read again
and that reading decides.

**Pending confirmation (ruled 8 October 2026).** When everything the phone reports fits the
recipe but the public sources cannot settle which device configuration it is, and nothing
else is missing, the verdict is also `not-ready`, with `pending_confirmation: true`. The
reason is one of `model-needs-confirmation`, `model-ambiguous-variant` or
`device-code-differs`, and `evidence.confirmation_request` carries the question for the
person. If any other check abstained, the verdict is `cannot-verify` instead. A pending
`not-ready` is never counted as a decided answer. Details:
`docs/reasoning/rulings-2026-10-08.md`.

### `cannot-verify`

**This is the default.** It is returned whenever `safe` cannot be established and
nothing specific has been found wrong. It is a first-class answer, not a failure,
and the reasons array must say which check abstained and why.

Reached when a required fingerprint field is absent or was inferred rather than
observed; the device is absent from the matrix; an asset cannot be tied to a model;
the recipe uses an operation the state model does not cover; model
coverage for this chipset family or partition scheme is insufficient; or required
prerequisite evidence is unconfirmed.

### `safe`

Every operation's preconditions are met by the fingerprint, every asset or target is
established as matching this device's model, and the modelled end state
is bootable.

**`safe` requires unanimity and confirming evidence.** It is emitted only when no
check failed *and* no check abstained. One abstention anywhere makes the verdict
`cannot-verify`.

**Safe requires a confirming fingerprint.** A recipe that merely declares an unlock
step or prerequisite is not safe on that basis. `safe` requires the fingerprint to
actively confirm the required state.

**What `safe` does not mean.** It is not a claim that the resulting system is good,
secure, supported, or that the person will like it. It is a claim about one thing:
that executing this recipe on this device is not expected to leave it unbootable.
Any interface presenting this verdict must say so in those terms.

---

## Prerequisites in v0.2

A prerequisite carries **STATE** with the declaring step as evidence (e.g. `state: "OPEN"`,
`required: "unlocked"`, `declared_by: "unlock_bootloader"`, `source_evidence: ...`).

**Which of those the verifier reads, and which it does not.** The verifier reads the
prerequisite's *key* (the fingerprint field it names) and `required`. It does not read
`state`, `declared_by` or `source_evidence`: those are provenance, carried so a human or a
later tool can trace a requirement back to the upstream step that declared it. Saying so
matters, because a contract that lists four fields without distinguishing them implies all
four participate in the verdict, and a reader would reasonably assume a recipe was checked
more thoroughly than it was.

`state` in particular is carried and unread today. If it is never going to be read it
should be dropped rather than decorate every recipe.

Absence of a prerequisite is not "none required". There are three distinct states:

1. **Absent from recipe (`prerequisites` omitted):** prerequisites unrecorded (`cannot-verify`).
2. **`prerequisites: null`:** prerequisite authoring state is null or invalid (`cannot-verify`).
3. **`prerequisites: {}`:** the recipe declares no prerequisites, but v0.2 has no proof that
   the procedure needs none (`cannot-verify`).

Only an explicit prerequisite block whose required states are confirmed by the fingerprint
can yield a `safe` verdict.

### Three kinds of unestablished prerequisite

When a prerequisite is not confirmed satisfied, there are three distinct reasons that must not blur into one:

- **`unknown`** — the field applies to this device and could not be established read-only.
  Already defined. Unchanged.
- **not establishable from the device, ever** (`unlock-out-of-band`) — the prerequisite is real,
  it is not satisfied-or-unsatisfied as far as any device property is concerned, and no better
  capture, no newer tool and no more patient tester will change that. The evidence sits in a
  vendor's database, an account portal, or an external tool (e.g. Xiaomi Mi Unlock, Motorola web
  portal, Fairphone support portal, Sony unlock site). This is a property of the **unlock method**,
  not of the capture, and it is therefore knowable from the recipe alone without any fingerprint
  at all.
- **absent** — neither of the above. The prerequisite block itself is missing or unrecorded.
  Never means "none required". Unchanged.

When an unlock prerequisite has `unlock_class: "out_of_band"`, the verifier emits the reason code
`unlock-out-of-band` with `outcome: "abstain"` (reason result `abstain`) and verdict
`cannot-verify`. It carries in the evidence block human-readable guidance stating what the person
must do out-of-band, and optionally a link to the authoritative upstream documentation.

---

## Hardware model matching

Ruled 16 September 2026, on the evidence in `docs/Research/variant-danger-findings.md`: a
recipe's identity is confirmed by the phone's model (`product_model`), not only its
codename, because one codename can cover several different models.

Ruled 8 October 2026: the recipe carries the public sources it rests on
(`target.models_sources`) and any configurations that share its codename
(`target.competing_sources`). Only sources on a domain listed in `data/vocabulary.json`
(`model_source_domains`) count. A model a credible source lists settles identity; a model
the sources do not list is `unsafe` on stock firmware; when the sources cannot settle it,
the verifier asks the person (see pending confirmation above). On custom firmware, identity
written by the ROM can confirm a recipe but never condemn one. Full table:
`docs/reasoning/rulings-2026-10-08.md`, section 4.

---

## Upstream untested flag and provenance gating

OpenAndroidInstaller configs carry an optional boolean `untested: true`, indicating
that a configuration was authored but never confirmed on physical hardware.

A recipe derived from an upstream configuration marked untested must **never reach `safe`**,
even when all fingerprint prerequisites and identity fields match cleanly.

### The rule

- **Recipe marked untested (`upstream_untested: true` / `"untested"`):** The verifier emits
  the reason code `recipe-untested-upstream` with outcome `abstain` and verdict
  `cannot-verify`. The reason message explicitly names upstream's statement about the
  configuration as the limit, distinguishing it from device or fingerprint uncertainty.
- **Recipe has not established it (`upstream_untested: "unestablished"` / `null` or omitted):**
  No effect. The verifier abstains only for whatever other reasons apply.

### Both halves and the open question

1. **The flag being SET is safe to act on today.** If upstream explicitly states a config was
   never confirmed on hardware, refusing `safe` is conservative and sound regardless of any
   other evidence.
2. **The flag being ABSENT is not yet a fact.** Absence represents "tested" only if upstream
   reliably clears `untested: true` once hardware verification is confirmed. The question was
   put to the OpenAndroidInstaller maintainers on 16 September 2026; no answer is recorded
   yet.

### Pending upstream resolution

- **If upstream confirms the flag is actively cleared upon hardware confirmation:** Absence
  of the flag becomes an established positive signal (upstream-tested).
- **If upstream indicates flags are stale or unmaintained:** Absence remains unestablished,
  and recipes without independent confirmation cannot be treated as tested on that basis alone.

Absence is not a value: an unrecorded or unestablished testing state must never be read as
"tested".

---

## Every verdict carries its evidence

The verifier output includes an `evidence` record carrying:
- the fingerprint `record_id`
- its `capture_timestamp` (or capture date)
- the list of `fields_consumed` by the verification procedure

The verifier sets **no expiry policy**. It states what it relied on and when;
staleness is the consumer's decision.

---

## Precedence

    unsafe  >  not-ready  >  cannot-verify  >  safe

Any identity check that fails makes the verdict `unsafe`, whatever else was found. An
unmet prerequisite on a phone whose identity is confirmed makes it `not-ready`, even if
another check abstained, because "not ready" is already a definite finding. A pending
confirmation makes it `not-ready` only when no other check abstained. Any check
abstaining makes the verdict at best `cannot-verify`. `safe` survives only unanimous
agreement.

---

## Error costs, which is why the asymmetry above exists

| Error | What happened | Cost | Gate |
|---|---|---|---|
| **false safe** | Said `safe`, recipe bricks the device | A device is destroyed and the project has no reason to exist | **Must be zero on the golden corpus. Build fails on one.** |
| false unsafe | Said `unsafe`, recipe was fine | Someone is inconvenienced and may route around the tool | Tracked, not gated |
| over-abstention | Said `cannot-verify` too often | The tool is useless, which is a real failure | `abstain_rate` reported alongside every result set |

A verifier that returns `cannot-verify` for everything has a perfect false-safe rate
and is worthless. Reporting abstain rate on every run is what stops the primary
metric being gamed by caution.

---

## Every verdict carries reasons

The verdict alone is not the output. Each `reasons[]` entry names the check, its
result (`pass` / `fail` / `unmet` / `abstain`), the fingerprint fields it relied on, a
stable machine-readable code, and since 24 September a `kind` and a `plain` sentence a
non-technical reader can follow, both from `data/reason_codes.json`.

Every abstention has one of two kinds, and the difference matters more than the count:

| Kind | Meaning | Example |
|---|---|---|
| `honest` | The phone or the world does not give the evidence. The tool is doing its job. | The phone did not report its storage layout. |
| `our_gap` | The recipe or the format is missing something this project can fix. | The recipe lists no starting conditions. |

`coverage.py` reports cannot-verify split by kind, so a reviewer can see how many
abstentions are the world being silent and how many are work left for us.

Every verdict object also carries `scope`: the question it answers, what it checked, and
what it did not check (the files you will flash, changes since the phone was read, steps the
recipe does not declare). Anything that renders a verdict has the scope in hand. Reason codes are part of the public interface: other
tools consume them, so they are versioned and not renamed casually.

`coverage` states what the model could and could not reason about for this device,
so a consumer can distinguish "checked and fine" from "not checked."

---

## Explicit non-goals

The verifier does not judge whether a ROM is trustworthy, well-built or maintained;
whether a bootloader *can* be unlocked when the device does not report it; whether
the device will be usable afterwards; or anything about the person's intent.

---

## Architectural constraint

Verification is a **pure function**. Fingerprint in, recipe in, verdict out. No
device I/O, no USB permission, no network, no filesystem writes on the verify path.

Ruled 24 September 2026: `verify()` stays a pure function in the sense that matters, **no
device I/O, and deterministic given its two arguments**. It reads three data files once at
import (`vocabulary.json`, `unlock_guidance.json`, `reason_codes.json`), refuses to start if
the vocabulary or the reason texts are missing, and never reads or writes anything while
verifying. `tests/test_verdict_v03.py` asserts the same inputs give the same output and are
not mutated.
Anything that talks to hardware lives in a separate module the verifier cannot call.

This is not defensive coding. It makes "the verifier bricked my phone" a sentence
that cannot be true, rather than an outcome that has to be prevented, and that is a
property worth stating in the grant application.

---

## Still open (11 October 2026)

- [ ] Reason code namespace and versioning policy.
- [ ] How fingerprint field confidence is represented, given the /e/OS codename case
      in `prior-art.md`. Observed / inferred / absent may not be enough.
- [ ] Whether `coverage` is a structured object or prose. Structured is better for
      consumers, more work to keep honest.
- [ ] Whether `unsafe` distinguishes "will brick" from "will fail harmlessly."
      Probably yes, but not in v1.
- [ ] Multi-slot active/inactive target modelling in v0.2 operations.
- [ ] Formal schema for open-vocabulary prerequisite state machines.
