# Verdict contract

**Status: specification. Written before implementation, deliberately. The code is
measured against this document, not the other way round.**

Version 0.2, 13 September 2026.

---

## What the verifier is asked

    verify(fingerprint, recipe) -> { verdict, reasons[], coverage, evidence }

`fingerprint` is what is known about one specific device, field by field, each field
carrying its provenance and whether it was actually observed.

`recipe` is an ordered sequence of provisioning operations plus references to the
assets they write or prerequisites they declare.

`verdict` is one of `safe`, `unsafe`, `cannot-verify`. There is no fourth value and
no numeric score in the output. A score invites a person to set their own threshold,
which relocates the safety decision to the least informed point in the system.

---

## The three verdicts

### `unsafe`

At least one condition has been **identified** under which executing this recipe on
this device would leave it unbootable or unrecoverable, or the recipe contains an
operation whose preconditions are provably unmet by this fingerprint.

Examples: an image built for a different model or variant; a bootloader written
before the sequence can complete; a slot assumption contradicted by the device's
actual partition scheme; an operation requiring an unlocked bootloader on a device
reporting locked.

`unsafe` is a positive finding. It requires evidence, not absence of evidence.

### `cannot-verify`

**This is the default.** It is returned whenever `safe` cannot be established and
nothing specific has been found wrong. It is a first-class answer, not a failure,
and the reasons array must say which check abstained and why.

Reached when a required fingerprint field is absent or was inferred rather than
observed; the device is absent from the matrix; an asset cannot be tied to a model
or variant; the recipe uses an operation the state model does not cover; model
coverage for this chipset family or partition scheme is insufficient; or required
variant or prerequisite evidence is unconfirmed.

### `safe`

Every operation's preconditions are met by the fingerprint, every asset or target is
established as matching this device's model and variant, and the modelled end state
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

## Graded variant matching

Variant matching is graded, and the verdict follows the evidence:

- **Exact variant match** -> `safe` or `unsafe` reachable.
- **Alias in `supported_device_codes`** -> `safe` or `unsafe` reachable, because upstream
  explicitly asserted the equivalence.
- **Partition and bootloader agree, variant unconfirmed** -> `cannot-verify`, naming
  `variant` as the missing evidence. **NEVER `safe`.**

This is not a fallback to a looser match on failure. That would make less evidence
produce a more permissive verdict, which is the false-safe pathway. It is a weaker
verdict for weaker evidence.

A human confirming the variant is **NEW EVIDENCE**, not inference. It moves a recipe to
the exact-match tier and must be recorded with its own provenance, the way the bench
kit records `identity_source`.

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

    unsafe  >  cannot-verify  >  safe

Any check returning `unsafe` makes the verdict `unsafe`, whatever else was found.
Any check abstaining makes the verdict at best `cannot-verify`. `safe` survives only
unanimous agreement.

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
result (`pass` / `fail` / `abstain`), the fingerprint fields it relied on, and a
stable machine-readable code. Reason codes are part of the public interface: other
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
Anything that talks to hardware lives in a separate module the verifier cannot call.

This is not defensive coding. It makes "the verifier bricked my phone" a sentence
that cannot be true, rather than an outcome that has to be prevented, and that is a
property worth stating in the grant application.

---

## Open in v0.2

- [ ] Reason code namespace and versioning policy.
- [ ] How fingerprint field confidence is represented, given the /e/OS codename case
      in `prior-art.md`. Observed / inferred / absent may not be enough.
- [ ] Whether `coverage` is a structured object or prose. Structured is better for
      consumers, more work to keep honest.
- [ ] Whether `unsafe` distinguishes "will brick" from "will fail harmlessly."
      Probably yes, but not in v1.
- [ ] Multi-slot active/inactive target modelling in v0.2 operations.
- [ ] Formal schema for open-vocabulary prerequisite state machines.
