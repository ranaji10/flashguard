# The gap between what a human says and what a verifier can establish

*Measured 6 September 2026, the first time the corpus was replayed through `verify()`.*

    recipe                    human says    verifier returns
    a5xelte-recovery          cannot-verify cannot-verify     agree
    avicii-multi-image        unsafe        cannot-verify     DISAGREE
    fp3-unlock                unsafe        cannot-verify     DISAGREE
    fp4                       unsafe        cannot-verify     DISAGREE
    kirin-unlock              unsafe        cannot-verify     DISAGREE

Four of five disagree. **Neither side is wrong.** They are answering different questions,
and the distance between them is the most useful thing this project has measured.

## Why they differ

The human read the real device config, saw that it requires an irreversible bootloader
unlock before the recovery write, saw that the recipe omits it, and concluded: **unsafe**.
Running this procedure as written would fail, or brick.

The verifier reads only the recipe. **Nothing in the recipe says a step is missing.** An
omission leaves no trace. So it cannot establish completeness, and it abstains:
**cannot-verify**.

Both are correct answers to their own question:

- *Is this procedure safe to run?* — No. It omits an irreversible prerequisite.
- *Can safety be established from this recipe?* — No. The evidence is not present.

## Why this must not be "fixed"

The obvious move is to adjust the corpus verdicts to `cannot-verify` so the numbers agree.
**That is tuning ground truth to the tool.** It is the same circularity `promote.py` refuses
when a descriptor's expected class came from the classifier's own answer, and the same
reason an abstention cannot be promoted to a fixture.

The second obvious move is to make the verifier return `unsafe` on these. It has no basis
for that: it would be guessing from the absence of evidence, which is the false-safe
pathway running in reverse and a habit that will produce a false safe eventually.

## What to record instead: two fields, not one

A recipe carries two assessments:

- **`human_assessment`** — what a person who read the real config concludes about the
  procedure. Requires knowledge the recipe does not contain.
- **`expected_verdict`** — what a correct verifier should return **given this recipe as
  written**. This is what the false-safe gate is measured against.

Where they differ, the recipe records why. That difference is a measurement:

> **information-loss rate**: the proportion of recipes where a human can reach a definite
> verdict and the verifier cannot.

Today that rate is 4 of 5. It is not a defect. It is a number describing how much
safety-relevant evidence the v0.1 format destroys, and it is the argument for what v0.2
must carry.

## The metric this makes honest

    false safes    0 of 5
    decided        0 of 5

Zero false safes with zero decided is the meaningless zero the coverage floor exists to
expose. Reported alone it looks like a pass. Reported as a pair it says plainly: **the
verifier currently decides nothing, so it cannot yet be wrong.**

Both numbers go in the proposal together, with the information-loss rate beside them. A
verifier that abstains honestly and says why is a defensible first result. A verifier
claiming zero false safes while deciding nothing is not.
