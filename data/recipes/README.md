# Test recipes (the "golden corpus")

A recipe describes the steps for installing software on one device model. These recipes are
the test cases the verifier is measured against. They live in two folders:

- `data/recipes/`: five recipes in the first format (v0.1), kept unchanged as evidence of
  what that format could not express (see `docs/reasoning/verdict-gap.md`).
- `data/recipes-v0.2/`: thirteen recipes in the current formats (v0.2 and v0.3), which also
  carry each recipe's prerequisites and the public sources for the device's model codes.

The format is described in `docs/reasoning/recipe-format.md`, with the v0.3 additions in
`docs/reasoning/rulings-2026-10-08.md`.

## Two labels on every recipe

- `human_assessment`: what a person reading the real upstream instructions concludes
  about running this procedure on this device.
- `expected_verdict`: what a correct verifier should answer from the recipe as written.

Each comes with a written reason (`expected_verdict_reason`, and `verdict_gap_reason` where
the two differ). They can differ, because a recipe may not carry everything a person can
see. How often they differ is reported as the "information loss" rate.

## The recipes

| File | Device | Format | Human assessment | Expected verdict |
|---|---|---|---|---|
| `a5xelte-recovery-independent-facts.json` | Samsung Galaxy A5 (2016) (`a5xelte`) | 0.1 | cannot-verify | cannot-verify |
| `avicii-multi-image-facts.json` | OnePlus Nord (`avicii`) | 0.1 | unsafe | cannot-verify |
| `fp3-unlock-independent-facts.json` | Fairphone 3 (`FP3`) | 0.1 | unsafe | cannot-verify |
| `fp4-independent-facts.json` | Fairphone 4 (`FP4`) | 0.1 | unsafe | cannot-verify |
| `kirin-unlock-independent-facts.json` | Sony Xperia 10 (`kirin`) | 0.1 | unsafe | cannot-verify |
| `a52sxq.json` | Samsung Galaxy A52s 5G (`a52sxq`) | 0.3 | safe | not-ready |
| `alioth.json` | POCO F3 (`alioth`), from LineageOS | 0.3 | not-ready | not-ready |
| `alioth-oai.json` | POCO F3 (`alioth`), from OpenAndroidInstaller | 0.3 | unsafe | unsafe |
| `a5xelte.json` | Samsung Galaxy A5 (2016) (`a5xelte`) | 0.2 | cannot-verify | cannot-verify |
| `avicii.json` | OnePlus Nord (`avicii`) | 0.2 | safe | cannot-verify |
| `fajita.json` | OnePlus 6T (`fajita`) | 0.3 | safe | not-ready |
| `figo.json` | Huawei P smart (`figo`) | 0.3 | cannot-verify | not-ready |
| `fp3.json` | Fairphone 3 (`FP3`) | 0.2 | unsafe | cannot-verify |
| `fp4.json` | Fairphone 4 (`FP4`) | 0.2 | unsafe | cannot-verify |
| `kirin.json` | Sony Xperia 10 (`kirin`) | 0.2 | unsafe | cannot-verify |
| `larry.json` | OnePlus Nord CE 3 Lite (`larry`) | 0.3 | safe | safe |
| `spacewar.json` | Nothing Phone (1) (`Spacewar`) | 0.2 | safe | safe |
| `star2lte.json` | Samsung Galaxy S9+ (`star2lte`) | 0.3 | safe | not-ready |

The expected verdict describes the recipe on its own. What the verifier actually answers
also depends on the phone it is checked against: for example, `larry` and `spacewar` return
`not-ready` against the real captured phones, because their bootloaders are locked.

**Added 17 October 2026.** `alioth-oai.json` is the first recipe expected to return `unsafe`:
OpenAndroidInstaller's config calls the POCO F3 a single-layout phone, while the phone reports
virtual A/B and LineageOS agrees with the phone. `figo.json` keeps a gap on record: the verifier
says not-ready (unlock first), but LineageOS states that no official unlock method exists for
this phone. `a52sxq` and `star2lte` moved from cannot-verify to not-ready through the layout
absence rule (`docs/reasoning/layout-absence-rule.md`). The labels of all three new recipes
rest on public sources only, like those of 8 October.

**Label review.** Most v0.2 labels were set with the help of an AI coding assistant, in the
same sitting as the verifier change they test. The labels of the three recipes added on
8 October 2026 (`larry`, `fajita`, `star2lte`) rest on public sources only. Ranaji has
deliberately not confirmed them, because he does not own these phones and cannot check
them in hand. They stay as they are until someone who can does.

## How results are measured

Run `python3 data/coverage.py`. For each format it reports:

    false safes        expected not-safe, answered safe     MUST BE ZERO. The build fails.
    decided share      share of definite answers            must stay at or above the floor
    information loss   human could decide, verifier could not

The floor is in `data/coverage-floor.json` and may only go up. Reporting the decided share
next to the false-safe count stops a verifier that refuses everything from looking good.

## Where recipes come from

Recipes are written from facts about each device published by OpenAndroidInstaller
(GPL-3.0-or-later configuration files) and the LineageOS wiki (CC BY-SA 3.0). Facts such as
codenames, model numbers and which unlock step is needed are stated independently; no
instruction text is copied. Every recipe names where its facts came from in its `source`
field. This folder is published under CC0 (`data/LICENSE`).

## Every miss becomes a permanent case

A wrong answer or a missed catch is added here as a new recipe with both labels, before the
rule that would have caught it is written. The corpus only grows.
