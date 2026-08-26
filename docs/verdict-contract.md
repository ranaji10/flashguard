# Verdict contract

**Status: specification. Written before implementation, deliberately. The code is
measured against this document, not the other way round.**

Version 0.1, 26 August 2026.

---

## What the verifier is asked

    verify(fingerprint, recipe) -> { verdict, reasons[], coverage }

`fingerprint` is what is known about one specific device, field by field, each field
carrying its provenance and whether it was actually observed.

`recipe` is an ordered sequence of provisioning operations plus references to the
assets they write.

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
or variant; the recipe uses an operation the state model does not cover; or model
coverage for this chipset family or partition scheme is insufficient.

### `safe`

Every operation's preconditions are met by the fingerprint, every asset is
established as matching this device's model and variant, and the modelled end state
is bootable.

**`safe` requires unanimity.** It is emitted only when no check failed *and* no
check abstained. One abstention anywhere makes the verdict `cannot-verify`.

**What `safe` does not mean.** It is not a claim that the resulting system is good,
secure, supported, or that the person will like it. It is a claim about one thing:
that executing this recipe on this device is not expected to leave it unbootable.
Any interface presenting this verdict must say so in those terms.

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

## Open questions

- [ ] Reason code namespace and versioning policy.
- [ ] How fingerprint field confidence is represented, given the /e/OS codename case
      in `prior-art.md`. Observed / inferred / absent may not be enough.
- [ ] Whether `coverage` is a structured object or prose. Structured is better for
      consumers, more work to keep honest.
- [ ] Whether `unsafe` distinguishes "will brick" from "will fail harmlessly."
      Probably yes, but not in v1.
