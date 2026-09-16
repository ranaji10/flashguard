# Batch 3 of 4, 16 September. A verdict for a prerequisite that is not on the device.

This batch touches the verifier, the schema and the verdict contract. It does not touch
`bench-kit/`. Run it after batches 1 and 2, or in parallel with them if you are a different
session, because the files do not overlap.

This is not a defect repair. It is the finding the LineageOS survey produced, turned into
something the verifier can say.

---

## The finding

Counted against the pinned LineageOS clone, by `install_method`, every classification
verified by reading the template: **348 of 737 devices, 47 percent, have an unlock whose
evidence is not on the device.** Xiaomi means the Mi Unlock Windows application, tied to an
account, with a waiting period. Motorola is a web portal. Fairphone is a support page.
Samsung's `samloader_rs` is Download Mode with no fastboot unlock step at all.

**No verifier reasoning from device state can ever establish that such a prerequisite is
satisfiable, because the evidence sits in a vendor's database.** That is a boundary on the
whole category of tool, and it is a different thing from a prerequisite that happened not to
be readable this time.

Today both collapse to `cannot-verify` with a reason that means "could not establish". A
tester with a Xiaomi is told the tool could not work something out, when the true answer is
that nothing about their phone could ever tell anyone, and here is what they have to go and
do by hand.

---

## 1. The verdict contract states the distinction first

Edit `docs/reasoning/verdict-contract.md` before touching code, because the code follows the
contract here rather than the other way round.

Add a section that separates three things that currently blur into one:

- **`unknown`** — the field applies to this device and could not be established read-only.
  Already defined. Unchanged.
- **not establishable from the device, ever** — the prerequisite is real, it is not
  satisfied-or-unsatisfied as far as any device property is concerned, and no better capture,
  no newer tool and no more patient tester will change that. This is new.
- **absent** — neither of the above. Already defined as never meaning "none required".
  Unchanged.

State plainly that the second one is a property of the **unlock method**, not of the capture,
and that it is therefore knowable from the recipe alone without any fingerprint at all.

## 2. A reason code of its own

Add `unlock-out-of-band` as a reason code. It is **not** a variant of the
"could not establish" family and must not share its text.

Rules:

- It carries `outcome: "abstain"`, because the verifier genuinely cannot decide. The verdict
  stays `cannot-verify`.
- It must be reachable **without** a fingerprint, since it depends only on what the recipe
  declares about the unlock method.
- It must never be reachable for a device whose unlock is a plain command, because that
  would abstain on the 170 devices where the answer is readable.

## 3. The recipe carries the unlock class

The recipe format needs one new field in the prerequisite block naming how the unlock is
obtained. Use the classification that already exists in
`docs/Research/install-method-classification.md`: at minimum `command` and `out_of_band`,
and `unknown` for a recipe where it has not been established.

**Absence is not a value here either.** A recipe that omits the field must not be read as
`command`. It abstains with the existing "could not establish" reason, not with
`unlock-out-of-band`.

**The licensing wall holds.** The classification, the counts and the field names cross it.
Template text and upstream YAML do not. Each recipe cites the source it consulted and states
its facts independently, exactly as the existing five do.

## 4. The verdict says what to do, not only that it cannot

This is the part Ranaji asked for and it is the point of the whole batch. When
`unlock-out-of-band` fires, the evidence block must carry a human-readable instruction
naming **what the person has to go and do**, in their own world: an account to create, a
portal to visit, a token to request, a waiting period to sit out.

Requirements:

- The text lives in **data**, keyed by unlock method, not in `verify.py` as a chain of
  `if` statements. One vendor's procedure changing must be a data edit.
- It states the steps and does not estimate how long they take, because we have not measured
  that and a wrong number here is worse than none.
- It never tells anyone to run a flashing command. Flashguard verifies; it does not execute.
- Where we do not have the steps for a method, the field is absent and the reason text says
  the unlock is out of band without inventing a procedure. Do not write a plausible one.

## 5. Tests

- A recipe declaring an out-of-band unlock returns `cannot-verify` with `unlock-out-of-band`
  **and no fingerprint supplied at all**.
- A recipe declaring a command unlock never returns `unlock-out-of-band`, fingerprint or not.
- A recipe omitting the field returns the existing could-not-establish reason and **not** the
  new one.
- The guidance text for a known method is present in the evidence; for an unknown method it
  is absent rather than empty or invented.
- Plant a defect that lets `unlock-out-of-band` fire on a command-class recipe, watch a test
  fail, restore it.

---

## What "done" means for this batch

- `bash tests/all.sh` runs and nothing that passed before fails now.
- The contract changed before the code, and says the same thing the code does.
- Every new test was proved to fail by planting a defect and removing it.
- No file under `bench-kit/` changed.
- `bash tests/check-public-safe.sh` still passes, and nothing under `library/` became tracked.

Do not report build status in a summary. Ranaji runs the suite himself.
