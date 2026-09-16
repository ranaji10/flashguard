# Batch 4 of 5, 16 September. Upstream marks its untested configs. Carry the flag.

*Amended 16 September after research task 3: one rule added about not merging this gate
with the one batch 5 will add.*

Smallest of the four, and the only one whose rule comes from upstream's own data rather than
from our judgement. Touches the recipes, the verifier and the contract. Does not touch
`bench-kit/`.

---

## The finding

OpenAndroidInstaller configs carry an optional, schema-declared boolean `untested: true`,
meaning the config was authored and never confirmed on real hardware. Around one config in
five carries it.

None of our five recipes records it. Their `source` blocks hold `device_facts_from`,
`consulted` and `authored`, and not this.

**A recipe derived from an untested upstream config must never reach `safe`.**

---

## Read this before you implement it, because half the rule is on hold

There are two halves and only one of them is settled.

- **The flag being SET is safe to act on today.** If upstream says a config was never
  confirmed on hardware, refusing to reach `safe` is conservative whatever else is true.
  Build this half now.
- **The flag being ABSENT is not yet a fact.** Absence means "tested" only if upstream clears
  the flag once someone confirms a device. Ranaji has asked them; they have not answered.

So: **absence is not a value.** A recipe whose `source` block does not carry the field must
not be treated as tested. It is `unknown`, and it does not gate anything yet.

Do not write code that assumes the absent case means tested, and do not leave a comment
saying it probably does.

---

## 1. The recipe carries the provenance

Add to each recipe's `source` block a field recording upstream's testing claim, with three
values: the config was marked untested, the config was not marked untested, or we have not
established it. Default for every existing recipe is the third, because nobody has looked
yet.

**The licensing wall holds.** A field name and a boolean cross it. Template text and upstream
YAML do not.

## 2. The verifier gates on it

- Recipe says upstream marked it untested: the verdict can never be `safe`. It is
  `cannot-verify` with a reason of its own naming the provenance, and that reason must not be
  confused with a missing prerequisite.
- Recipe says not marked untested: no effect today. It is not a licence to upgrade anything.
- Recipe has not established it: no effect. Abstains for whatever other reason applies.

The reason code must say the limit is **upstream's own statement about the config**, not
something about the device. A tester whose phone is fine deserves to know the recipe is the
uncertain part.

**Do not build a general provenance gate.** Batch 5 will add a second, independent limit on
`safe` — whether the device's model is one the recipe covers — and it is tempting to write one
mechanism that both feed into. Resist it. They fail for different reasons, they need different
reason codes, and a person told "this cannot be called safe" deserves to know which of the two
it was. Either one alone blocks `safe`; neither cancels the other.

**Stay inside the `source` block.** Batch 3 is editing the prerequisite block and batch 5 will
edit `target`. Three producers in three parts of one schema is fine; three in one part is a
merge conflict nobody notices until a recipe quietly loses a field.

## 3. The contract records both halves

In `docs/reasoning/verdict-contract.md`, write the rule **and** the open question: that the
absent case is undecided pending an answer from OpenAndroidInstaller, and what we will do
with each possible answer. A rule with a known hole is honest; a rule that hides the hole is
the thing this project keeps finding in other people's code.

## 4. Tests

- A recipe marked untested cannot return `safe` even when every prerequisite is confirmed by
  a fingerprint. This is the important one: build the fingerprint that would otherwise
  produce `safe` and assert it does not.
- A recipe marked not-untested returns exactly what it returned before the change. Assert the
  reason codes are byte-identical, not merely that the verdict matches.
- A recipe with the field absent returns exactly what it returned before the change.
- Plant a defect that lets an untested recipe reach `safe`, watch the test fail, restore it.

---

## What "done" means for this batch

- `bash tests/all.sh` runs and nothing that passed before fails now.
- The safe-blocking test was proved to fail on a planted defect.
- Nothing in the code or comments assumes the absent case means tested.
- `bash tests/check-public-safe.sh` still passes, and nothing under `library/` became tracked.

Do not report build status in a summary. Ranaji runs the suite himself.
