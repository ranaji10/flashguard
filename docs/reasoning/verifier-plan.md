# The verifier: what it is, and what "done" means

*Written 6 September 2026. The verifier does not exist. This file is the specification that
makes that fact actionable rather than just true.*

**Read `docs/reasoning/verdict-contract.md` first.** That is the contract; this is the plan
for satisfying it.

## The state of things

The repository is roughly 6,400 lines and none of them are the verifier. There is no
`verify(fingerprint, recipe)`. `data/recipes/` holds a README. The false-safe rate — the
primary metric, the build gate, the centre of the proposal — has no subject to measure.

Everything built so far is instrumentation for collecting the **inputs** to a function
nobody has written. Good instrumentation: it found real defects and produced a complete
seven-field record. But it is not the thing the grant funds.

## Three things that are easy to conflate

| | What it is | Where it lives | State |
|---|---|---|---|
| **Fingerprint** | What a real device reports: model, chipset, partition scheme, bootloader state | `data/device-matrix.jsonl` | 1 complete, 3 partial |
| **Corpus** | Provisioning recipes with human-established verdicts | `data/recipes/` | **empty** |
| **Verifier** | The function between them | nowhere | **does not exist** |

The corpus is the harder of the two missing pieces, because a recipe without a
human-established verdict tests nothing.

## Done, for a first version

1. **A pure function** matching `docs/reasoning/verdict-contract.md`: fingerprint in, recipe
   in, `safe` / `unsafe` / `cannot-verify` out. No device I/O, no network, no filesystem on
   the verify path. Same shape as `classify.sh` and `derive.sh`, for the same reason: a
   function that needs hardware in your hand gets tested once and then trusted forever.
2. **Ten recipes in `data/recipes/`**, five safe and five deliberately unsafe, each carrying
   the reason a human assigned its verdict. Deliberately unsafe means unsafe in a way that
   is *plausible*: a wrong device codename, a recipe for the A/B variant applied to the
   single-partition one, a locked bootloader assumed unlocked.
3. **The false-safe gate wired into `tests/all.sh`**, failing the build on a single false
   safe.
4. **The coverage floor reported alongside it.** See below.

Roughly 200 to 300 lines. Tier A being incomplete does not block it: the verifier takes a
fingerprint as *input*, and there is one real complete fingerprint plus a schema to write
against.

## The metric has to be a pair

A verifier that answers `cannot-verify` for everything has a false-safe rate of exactly
zero. A reviewer sees this in seconds, and both independent research runs raised it.

So `data/coverage.py` reports two numbers and the build fails if either is missed:

    false_safe        == 0        the gate
    decided_share     >= X        the floor

`decided_share` is the proportion of corpus recipes given a definite `safe` or `unsafe`
rather than `cannot-verify`. **X gets chosen once the corpus exists** and there is something
real to measure — naming a number now would be a guess dressed as a target.

Both are stated in the proposal as a pair, so "zero false safes" can never be read as "it
refuses everything".

## What false-safe is measured against

Zero is meaningless without labelled ground truth, and this is the first question a reviewer
scoring technical feasibility will ask.

The corpus entries carry their verdict *and the human reason for it*. The largest unsolved
question in the plan is whether those verdicts can be derived consistently from
OpenAndroidInstaller's device configs at all. There is a concrete one-evening test for it:
take ten of their configs, hand-label the expected verdict for each by reading the config
against a device the matrix knows, and see whether it can be done consistently from the
config alone. **If a human cannot, no verifier will.** That experiment should happen before
the corpus is built, not after.

## What this is not

Not capability inference. Not path generation. Not a probability score. Not a flashing tool.
Each of those is RePurpose, and `CLAUDE.md` treats a proposal to add one as out of scope.

## The corpus has no `safe` recipe, and that may not be an oversight

*Noted 6 September 2026, after the first five recipes were written from real
OpenAndroidInstaller configs.*

    unsafe         4
    cannot-verify  1
    safe           0

Every recipe written from a real device config came out `unsafe` or `cannot-verify`. None
came out `safe`.

That could mean the five configs happened to be dangerous ones. It could also mean
something worse: **the v0.1 format cannot express a procedure that is genuinely safe.** The
findings record that prerequisites, unlock state, temporary boots and slot relationships
are all dropped. A recipe missing its preconditions is one a careful verifier must refuse,
so the format may be structurally incapable of producing a safe case.

If that is true, the verifier is a no-op: it abstains or refuses, always, and the false-safe
rate is zero for the reason that makes it meaningless.

**This must be settled before, or as part of, the first implementation.** The question is
not "write a safe recipe" — it is: *can a safe recipe exist in this format at all, and if
not, what minimum addition makes one possible?* Answering it by inventing a synthetic recipe
that happens to pass would be the corpus equivalent of a test that passes against a stub.
