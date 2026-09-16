# Research task 3 — does `product_device` hide a difference that can hurt someone?

Written 16 September. This task exists to settle a decision, not to gather background. Read
the decision first so you know what a useful answer looks like.

## The decision waiting on you

`flashguard/verify.py` checks a recipe field called `variant` against a fingerprint field of
the same name. No fingerprint has ever carried that field, so the check abstains on every
record. The ruling is between dropping the concept, defining it properly, or keeping it and
changing only the wording.

**Part of this has already been answered and you should not redo it.** Against the pinned
LineageOS clone:

- 493 of 737 device pages declare a `models:` list. Those values are `ro.product.model`
  strings.
- 268 of those 493 list **more than one model under one codename**. `a5xelte` lists eight.
  `klte` lists eight. `hero2lte` lists six.
- Both real captures in `data/contributions/rana-2026-08-29-rerun.jsonl` already carry
  `product_model`, and both match their device page exactly: `SM-A510F` is in `a5xelte`'s
  list, and `A063` is `Spacewar`'s only entry.

So the discriminator exists, upstream publishes it, and we already capture it. **That half is
settled. Do not re-count it.**

What is not settled is whether the difference between two models under one codename is ever
**dangerous**, and that is the whole question. If it never is, the honest answer is that
`product_device` is sufficient and the variant concept should go. If it sometimes is, the
verifier needs to check the model and the recipe needs to carry the list.

## The three questions, in priority order

### Q1. Where two models share a codename, does anything upstream treat them differently?

The highest-value question. For every codename declaring more than one model, look for any
upstream signal that the models are not interchangeable:

- per-model warnings, notes or caveats in the device page or its install instructions
- a `quirks` entry that names a model rather than the codename
- different `before_install`, `before_recovery_install` or firmware requirements
- install instructions that branch on the model, the carrier or the region
- known-bricking notes, "do not flash this on X" text, or modem and radio warnings
- any model listed on one codename page and also on a different codename page

Report the count of codenames where you found something, and name every one of them with
what you found. A handful of real examples is worth more than a percentage.

### Q2. Is there a case where flashing the wrong model of the right codename caused damage?

Search beyond the wiki: OpenAndroidInstaller issues and pull requests, LineageOS Gerrit,
XDA threads, bug trackers. You are looking for an account of someone flashing a build for
codename X onto a device that reports codename X but a different model, and something being
lost: the modem, the IMEI, the ability to boot, the ability to recover.

**Report what you cannot find as clearly as what you can.** "Searched these sources, found no
documented case" is a real answer here and it argues for dropping the concept. Do not pad a
negative result into a maybe.

### Q3. If the field stays with only its wording changed, what breaks?

The weakest of the three and worth a short section. If `variant` remains in the recipe format
and the only change is that the reason text stops implying the device failed to report
something, is there any way that becomes misleading later? In particular: does a field that
is present, unread and permanently abstaining risk someone in future wiring a check to it,
the way `identity_source` was once read as variant confirmation?

## Rules

- **The licensing wall.** The LineageOS wiki is CC BY-SA 3.0 and OpenAndroidInstaller is GPL.
  Counts, field names, codenames, model numbers and your own descriptions cross into this
  repository. Verbatim template text, instruction prose and YAML do not. Quote nothing you
  would not be comfortable seeing in a CC0 file.
- **Say which claims you verified and how.** A number you counted against the clone and a
  number you read in a forum post are not the same kind of fact and must not be presented the
  same way.
- **Correct the brief if it is wrong.** The previous two tasks both overturned something they
  were told, and that was the most valuable thing each of them did.
- **Do not decide.** End with the evidence for each of the three options and what it would
  take to be wrong. The ruling is Ranaji's.

## Where the output goes

Write one markdown file at `docs/Research/variant-danger-findings.md`, path relative to the
repository root. Do not write an absolute path, a home directory or a user name into any
file: this repository is public.
