# Golden corpus

Every recipe here carries an `expected` verdict. The runner produces actual verdicts
for all of them, appends the results to a log that is never rewritten, and fails the
build if a single **false safe** appears.

    false_safe    expected unsafe, got safe        MUST BE ZERO. Build fails.
    false_unsafe  expected safe, got unsafe        tracked
    abstain_rate  share answered cannot-verify     reported alongside, always

Reporting abstain rate is what stops the primary metric being gamed by a verifier
that refuses everything.

## Seed cases

| id | Expected | Case |
|---|---|---|
| `good-01` | safe | Valid recipe for a known device |
| `bad-boot-order-01` | unsafe | Flashes bootloader, then fails to complete |
| `bad-wrong-image-01` | unsafe | Image for a different model or variant |
| `bad-slot-assumption-01` | unsafe | Assumes A/B on a single-partition device |
| `bad-locked-bootloader-01` | unsafe | Operation needs unlock, device reports locked |
| `cannotverify-01` | cannot-verify | Device and recipe the matrix has no data for |
| `cannotverify-codename-01` | cannot-verify | Codename nearly matches but carries a regional suffix. See the /e/OS case in `docs/prior-art.md`. |

## Growing it without owning hardware

This is the answer to the corpus problem. Recipes are not devices, and recipes are
published.

- **OpenAndroidInstaller** publishes per-device configuration files for 88 devices
  under GPL-3.0-or-later. Real recipes, structured, for real hardware.
- **LineageOS** publishes per-device install instructions for hundreds of models.
- **postmarketOS** maintains a categorised device support matrix.

Import them, derive expected verdicts, and the verifier can be validated against
hundreds of genuine recipes on day one. Physical devices are then reserved for the
one thing only hardware gives you: the read-only fingerprint at Tier A.

Respect the source licences. GPL-3.0-or-later on the OpenAndroidInstaller material is
one of the arguments for the same licence here.

## Every miss becomes a permanent case

A misclassification or a missed catch is added here as a new recipe with its expected
verdict, before the rule that would have caught it is written. The corpus only grows.
