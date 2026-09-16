# Batch 5 of 5, 16 September. Replace `variant` with a model allowlist.

**AUTHORISED 16 September. Ranaji ruled Option B on the evidence in research task 3.** This file
was written and held; the hold is lifted. Run it after batch 4, not alongside it: both edit
`flashguard/verify.py` and both edit the recipe JSON files.

Research task 3 produced the evidence: `docs/Research/variant-danger-findings.md`.

---

## What the research established

**Q2 came back yes, with named devices and named failure modes.** Cross-flashing across models
that share one codename is documented to destroy hardware:

- **LG V30 `joan`:** the T-Mobile `H932` uses different signing keys and anti-rollback fuse
  definitions from the open-market `US998` and `H930`. Standard cross-flashing blows ARB fuses
  and hard-bricks the device into Qualcomm EDL 9008, requiring a board replacement.
- **Samsung Galaxy S5 `klte`:** one codename covering eight models including Verizon, Sprint and
  T-Mobile hardware. Flashing GSM modem binaries onto a CDMA model corrupts `efs`, zeroes the
  IMEI, or produces a modem crash loop.
- **Motorola `nash`, `clark`:** cross-flashing radio firmware across XT model variants corrupts
  `modemst1` and `modemst2`, erasing RF calibration into an unrecoverable state.
- **Samsung `a5xelte`:** regional models within the codename can differ in partition table
  geometry. **This is the codename of our one paired recipe.**

**And `product_device` does not even select a unique recipe.** Upstream splits 89 codenames into
220 separate device pages that all carry the same `codename` value and differ only by their
`models:` list — `miatoll` and `Mi8937` have six pages each, `garnet` five. So for 220 of the 737
pages, roughly 30 percent of the catalogue, a device reporting its codename maps to between two
and six different sets of firmware prerequisites. Upstream could not express them as one page.

**The discriminator is already captured.** `product_model` is one of the nineteen fields every
fingerprint carries, and both real captures match their upstream page exactly: `SM-A510F` is one
of `a5xelte`'s eight, `A063` is `Spacewar`'s only entry.

---

## 1. Replace the `variant` concept with a model allowlist

In the recipe `target` block, replace `variant` with a list of the `ro.product.model` strings the
recipe covers.

- **Absence is not a value.** A recipe with no list does not mean "covers every model". It means
  nobody has established which models it covers, and it abstains with a reason saying so. Do not
  let an empty list mean "all".
- **Exact strings only, no patterns.** Upstream uses exact strings with zero wildcards across all
  493 files that declare models. A prefix match would reintroduce the exact inference this whole
  finding is about.
- **The licensing wall holds.** Model strings, counts and codenames are facts and cross it.
  Upstream instruction prose and YAML do not. Each recipe cites the source it consulted and
  states its facts independently, as the existing five do.

## 2. Three outcomes, and the middle one is the point

| fingerprint `product_model` | recipe list | verdict |
|---|---|---|
| present, in the list | present | the check passes; `safe` stays reachable |
| present, **not** in the list | present | **`unsafe`**, and it is a hard fail, not an abstention |
| absent or `unknown` | present | abstain, with a reason naming `product_model` |
| anything | absent | abstain, with a reason saying the recipe's model coverage is unestablished |

Row two is the whole batch. A device whose codename matches and whose model is not covered is the
`H932` case, and the honest answer is not "I cannot tell". The recipe says which models it covers
and this is not one of them.

## 3. `variant` lives in two places, not one

This is the part most likely to be missed. `variant` is not only a `target` field.

```
flashguard/verify.py:93    every asset must carry ("asset_id", "role", "product_device", "variant")
flashguard/verify.py:160   for key in ("product_device", "variant"): asset[key] must equal target[key]
```

So every **asset** is required to carry `variant`, and an asset whose `variant` differs from the
target's produces `asset-variant-mismatch` and an `unsafe` verdict. Since `target.variant` equals
`target.product_device` in all five recipes, that loop currently compares one identifier twice.

Whatever happens to `variant`, both sites change together, and the asset rule has to be restated
rather than deleted: an asset must still be pinned to the identity it was built for. Decide
explicitly whether an asset is pinned per codename or per model, and write the answer down. Do
not leave one site changed and the other carrying a field nothing sets.

## 4. Remove the DISPUTED marker, because the ruling dissolves it

`flashguard/verify.py:290` carries the repository's only open `DISPUTED:` marker, asking whether
`supported_device_codes` is a variant-level or a family-level claim. **The ruling settles it by
making the question unnecessary rather than by answering it.**

Identity is now confirmed by matching the fingerprint's `product_model` against the recipe's model
list. So `supported_device_codes` no longer has to carry any claim about the variant at all: it
goes back to being what it always was, a list of device codenames a recipe covers, useful for
finding the right recipe and not for confirming the hardware in someone's hand.

Remove the marker **and write down why**, in the same place, in three lines: the question was
whether an alias hit could confirm a variant; it no longer needs to, because the model is checked
directly; ruled by Ranaji on 16 September on the evidence in `docs/Research/variant-danger-findings.md`.

Do not delete it silently. The convention in `.github/copilot-instructions.md` is that a
disagreement is never resolved by rewriting the question, and a marker that vanishes without a
record looks exactly like one that was rewritten away.

After this batch `bash tests/check-disputed.sh` should report zero open disagreements.

## 5. Two false-safe paths left by batches 3 and 4, both reproduced

Batch 3 shipped a false safe and the checker caught it, which is the third time that has
happened here and the third time it was caught. These two are what is left, and **both are
reachable by the recipes this batch is about to write.** Fix them before writing any recipe.

### 5a. The unlock gate is keyed on one hard-coded prerequisite name

```
flashguard/verify.py:18    _UNLOCK_PREREQUISITE_NAME = "bootloader_unlocked"
flashguard/verify.py:418   if name == _UNLOCK_PREREQUISITE_NAME and unlock_class != "command":
```

Against `BASE_RECIPE` the fix works: omitted, `"unknown"` and malformed `unlock_class` all
return `cannot-verify` with `missing-bootloader_unlocked`, `out_of_band` returns
`unlock-out-of-band`, and `command` still returns `safe`. All four verified.

**Rename the prerequisite and the false safe comes straight back.** I took `BASE_RECIPE`, renamed
`bootloader_unlocked` to `oem_unlocking_enabled`, dropped `unlock_class`, mirrored the fingerprint
key, and ran it:

```
verdict: safe
reasons: match-product_device pass, match-partition_scheme pass,
         prerequisite-oem_unlocking_enabled-confirmed pass
```

The commit that fixed it says so itself: *"the schema has no formal way yet to mark a prerequisite
as an unlock step."* That is the defect, and it stops being theoretical the moment a recipe is
written from a different upstream vocabulary. `oem_unlocking_enabled` is an Android setting name,
not an invention.

**Fix: mark the unlock step in the recipe, do not infer it from a name.** Add an explicit marker
to the prerequisite, and make the verifier abstain when a recipe declares an `unlock_bootloader`
operation and no prerequisite carries that marker. An unfindable unlock step must be loud, not
absent.

**Do not use `declared_by` for this**, tempting as it is: it already carries
`"unlock_bootloader"`. It is provenance, the contract says provenance is legitimately unread, and
reading a provenance field as a safety input is precisely what `identity_source` did on
13 September on the path to `safe`.

### 5b. The untested gate allowlists the wrong direction

```
flashguard/verify.py:459   if upstream_untested in (True, "untested", "true", "marked_untested"):
```

It lists the values that BLOCK. Everything else reaches `safe`. The documented vocabulary is
`true | false | "unestablished"`, and those three behave correctly — but anything outside it does
not:

```
upstream_untested = "marked"   ->  safe
```

A typo in a hand-written recipe — `"True"`, `"yes"`, `"marked untested"` — silently means "not
untested". **This is the same defect batch 3's checker just caught one file away**, where absent,
`"unknown"` and malformed `unlock_class` all fell through to the permissive branch. It was fixed
there and shipped here.

**Fix: allowlist the values that PERMIT.** Only an explicit `false` and `"unestablished"` may pass;
everything else abstains, with a reason that distinguishes "upstream marked this untested" from
"this recipe's testing claim is not a value I recognise". The second is a recipe defect and should
read like one.

**While you are there:** lines 456-457 fall back to a second field name, `source.untested`, if
`upstream_untested` is absent. One thing under two names is what this whole batch exists to undo.
Pick one, and if the fallback is kept for older recipes, say for how long in a comment.

### 5c. Prove both

- Rename the unlock prerequisite in a test recipe, omit `unlock_class`, assert `cannot-verify`.
- Declare an `unlock_bootloader` operation with no marked unlock prerequisite, assert
  `cannot-verify` and not `safe`.
- Set `upstream_untested` to a value outside the vocabulary, assert `cannot-verify` with the
  recipe-defect reason.
- And keep a test that `command` plus a confirming fingerprint still reaches `safe`, so the fixes
  are not just making everything abstain.

Plant each defect back and watch the test fail before you call it done.

## 6. The reason codes stay separate

Batch 4 adds a gate on upstream's `untested` flag. This one adds a gate on model coverage. They
fail for different reasons and must not share a reason code or a mechanism. Either alone blocks
`safe`; neither cancels the other.

## 7. Tests

- A fingerprint whose model is in the recipe's list, with every prerequisite confirmed, returns
  `safe`. Without this the batch has only made the verifier stricter.
- A fingerprint whose **codename matches and whose model is not in the list** returns `unsafe`.
  Build it from the real `a5xelte` capture with the model changed to another of that codename's
  eight, because that is the real shape of the hazard.
- A fingerprint with `product_model` absent or `unknown` abstains, and does **not** return
  `unsafe`. Not knowing the model is not the same as knowing it is wrong.
- A recipe with no model list abstains, and does not pass.
- The asset identity check behaves as section 3 decides, with a test for the mismatch case.
- Plant a defect that lets an uncovered model reach `safe`, watch a test fail, restore it.

## 8. Two recipes to write while you are here

- **`Spacewar`** is a single-model codename (`A063`), command-class unlock, A/B, and there is a
  real capture with all seven fields. It is the clean first case.
- **`a5xelte`** already exists and is on an eight-model codename. Add `SM-A510F` and whichever
  others the source actually covers, and let the existing pairing keep working.

---

## What "done" means for this batch

- `bash tests/all.sh` runs and nothing that passed before fails now.
- Every new test was proved to fail by planting a defect and removing it.
- No field named `variant` is left in the recipe format, the schema or the verifier unless
  section 3's decision deliberately keeps it, in which case the decision is written down.
- `bash tests/check-public-safe.sh` still passes and nothing under `library/` became tracked.

Do not report build status in a summary. Ranaji runs the suite himself.
