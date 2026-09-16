# Batch 3 of 5, 16 September. A verdict for a prerequisite that is not on the device.

*Amended 16 September after research task 3: one requirement added to section 4, and a
sequencing rule at the end. Both exist so this batch does not have to be rebuilt.*

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
- **The guidance must be able to say that a procedure does not apply to this device at all**,
  not only that the person has an unlock to go and obtain. Upstream publishes exactly that, in
  prose, on real devices: the Motorola Moto Z2 Force page warns that firmware for the wrong
  carrier model is likely to damage the device; the HTC 10 page excludes the Sprint and Verizon
  variants outright; the OnePlus firmware pages exclude carrier-branded models. If the guidance
  is keyed only by unlock method it cannot carry a model-scoped exclusion, and it will have to
  be rebuilt when the model check lands. Key it so that a second dimension can be added without
  moving what is already there. **Do not build the model check in this batch.** It is batch 5
  and it is waiting on a ruling.

## 5. The guidance may carry a link out, and a way back in

Ranaji asked whether the tool could send a person to the upstream page, let them do the steps
there, and take them back. Yes, and it is one more field rather than a new mechanism.

- Each guidance entry may carry a **link** to the upstream page that documents the procedure,
  alongside the steps. Sending someone to the authoritative page is better than paraphrasing it,
  and it sidesteps reproducing prose we did not write.
- **What comes back must be read from the device, never ticked by the person.** After the
  out-of-band steps, the phone is plugged in again and the bootloader state is read again. That
  is evidence. A checkbox saying "I unlocked it" is a tester asserting a fact about hardware,
  which is the shape this project already closed once, when a tester naming a device was read as
  confirming its variant.
- A checklist is therefore **navigation**, not evidence: it shows the person where they are in a
  procedure the tool cannot watch. Build it as progress, and let the re-read decide the verdict.
- Where a step genuinely cannot be re-read from the device — a vendor account, an approved
  application — it is recorded as a **claim with its source**, the way `browser_enumeration`
  records `tester`, and it can never lift the verdict above `cannot-verify`.

## 6. One line carried over from batch 2b

`bench-kit/START-HERE.html`, in `buildRecord`, ends its `host_shell` fallback with a guess:

```
var hostSh = (cur && cur.host_shell) || (S && S.host_shell) || (hostPlat === "windows" ? "powershell" : "not_applicable");
```

On Windows, with no shell recorded anywhere, that invents `powershell`. **It is not reachable
through the shipped page today** — every route sets `cur.host_shell`, and the default state
carries `host_shell: "not_applicable"`, which `Object.assign` preserves across a restored
session. Checked by exercising `buildRecord` in node against a fresh state, a stale state with
the key absent, and an empty string; all three reach the guess only when called directly.

So this is a guess sitting in the code waiting for a path, not a live defect. It is in this
batch because it is one line and because an unreachable branch that encodes an assumption is
exactly what shipped a false safe on 13 September.

**Two parts, and the first is the reason the second exists.** `host_shell` has no value meaning
"this was Windows and the shell was not established". Its three values are `powershell`, `cmd`
and `not_applicable`, and on Windows the field *does* apply, so `not_applicable` is wrong and a
guess is worse.

1. Add `unknown` to `host_shell` in `data/schema.md`, meaning exactly what it means everywhere
   else in that document: it applies and could not be established.
2. Replace the guess with `unknown`. The non-Windows case is already forced to
   `not_applicable` by the line below it, so the fallback only has to answer the Windows case.

The schema-agreement test added in 2b will pick up the new value automatically, because it reads
the schema text rather than a copy of the list. Add one assertion that a Windows record with no
shell recorded comes back `unknown` and not `powershell`.

## 7. Stay inside the prerequisite block

Batch 5 will add a field to the recipe's `target` block, and batch 4 adds one to `source`.
Confine every recipe change in this batch to the **prerequisite block**. Three producers editing
three parts of one schema is fine; three producers editing one part of it is a merge conflict
nobody will notice until a recipe silently loses a field.

## 8. Tests

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
