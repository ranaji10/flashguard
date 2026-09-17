# Recipe format

**Status: specification for verifier v0.1.** This format is deliberately small: it
describes the facts the verifier must check, without pretending to be a flashing
script or executable command list.

## Location and loading

Recipes are JSON objects stored as one file under `data/recipes/`. The verifier is
implemented in `flashguard/verify.py`, with `flashguard/__init__.py` re-exporting
`verify`. Tests import it as `from flashguard import verify`; the verify path itself
reads no files. Callers load and validate a recipe before passing the resulting
object to `verify(fingerprint, recipe)`.

## Shape

```json
{
  "schema_version": "0.1",
  "recipe_id": "pixel-system-only",
  "target": {
    "product_device": "oriole",
    "models": ["GD1YQ", "G9S9B"],
    "partition_scheme": "A/B"
  },
  "assets": [
    {
      "asset_id": "system",
      "role": "system",
      "product_device": "oriole"
    }
  ],
  "operations": [
    {
      "kind": "write-image",
      "partition": "system",
      "asset_id": "system"
    }
  ]
}
```

`schema_version`, `recipe_id`, `target`, `assets`, and `operations` are required.
`target` requires `product_device` and `partition_scheme`, and contains `models`
(an explicit allowlist of supported `ro.product.model` strings). Each asset
requires `asset_id`, `role`, and `product_device` (pinned per codename); asset IDs are unique.
Each operation requires `kind`, `partition`, and `asset_id`, and its asset ID must
refer to an entry in `assets`. Operation order is significant.

Corpus recipes carry two assessments:

- `human_assessment` is what a person who read the real device config concludes
  about the procedure.
- `expected_verdict` is what a correct verifier should return given the recipe as
  written. It is the only assessment used by the false-safe gate.

Both are one of `safe`, `unsafe`, or `cannot-verify`. `expected_verdict_reason`
records why the human assigned the verifier expectation. When the two assessments
are equal, `verdict_gap_reason` is still required to state why the recipe carries
no information loss for that case. When they differ, it names what the format could
not carry. A recipe with an incomplete translation of a source procedure must not
receive `safe` merely because the omitted steps are absent from its own operations.

Version 0.1 supports only the declarative `write-image` operation. It names a
partition and an already-identified asset; it contains no shell, fastboot, adb, or
filesystem command. Unknown operation kinds are outside the model and therefore
produce `cannot-verify`, rather than being guessed at.

## Version 0.2 addition

Version 0.2 keeps the v0.1 fields valid and adds `prerequisites`,
`install_method`, and `source_fields_unused`. It drops `assets` and
`operations.asset_id`; operations remain declarative `{kind, partition}` records.
Each prerequisite is an object with open-vocabulary `state`, `required`,
`declared_by`, `source_evidence`, and the unlock classification fields `unlock_class`
(`command | out_of_band | unknown`) and optional `unlock_method`. A declaration is not
fingerprint evidence: `safe` requires the fingerprint to confirm every required state.
When `unlock_class` is `out_of_band`, the prerequisite is not establishable from device state,
and the verifier emits `unlock-out-of-band` (`cannot-verify`) with out-of-band guidance in
the evidence block. Absence of `unlock_class` is not `command`: an omitted field abstains with
the generic missing prerequisite reason.

The `prerequisites` key has three distinct meanings: absent means the author did
not record whether prerequisites were considered; `{}` means the author declares
that none are needed; and `null` is invalid because the authoring state is not
machine-checkable. The verifier must preserve those distinctions.

The target and every referenced asset carry device identity because a recipe can
be structurally valid while an image belongs to another model or variant. The
partition scheme is explicit because an A/B assumption must not be inferred from
an absent fingerprint field. This shape is enough to test the first safety boundary
without inventing command syntax or claiming that asset contents are trustworthy.

## Provenance is required, and it is a licensing constraint

*Added 6 September 2026, before the corpus was built.*

Every recipe carries a `source` block. It is not decoration:

```json
"source": {
  "device_facts_from": "https://github.com/openandroidinstaller-dev/openandroidinstaller/blob/main/openandroidinstaller/assets/configs/oriole.yaml",
  "consulted": "2026-09-06",
  "authored": "independent",
  "upstream_untested": "unestablished",
  "verdict_reason": "why a human assigned this verdict"
}
```

`upstream_untested` records upstream's testing claim across the licensing boundary:
`true` (marked untested upstream), `false` (not marked untested), or `"unestablished"`
(default, uninspected/unknown).

`authored` is one of:

- **`independent`** — a human read the device facts (codename, partition scheme, which
  images exist) and wrote the recipe from them. Facts about a device are not authored
  works. This is the only value the corpus should normally carry.
- **`derived`** — the recipe is a transformation of someone else's file. **This creates a
  derivative work and the upstream licence follows it.**

### Why this matters more than it looks

`data/LICENSE` puts the recipe corpus under **CC0**. OpenAndroidInstaller's device configs
are **GPL**. A CC0 corpus mechanically derived from GPL configs is not a corpus you are
free to license that way, and the whole Q7 adoption argument — that postmarketOS,
LineageOS and others can absorb this with no friction — rests on CC0 being real.

The resolution is not a legal opinion. It is a working practice: **write recipes from device
facts, citing the config as the place those facts were checked, rather than transforming the
config file into a recipe.** That is also better research practice, because a recipe you
wrote is a recipe you understood, and a recipe you transformed is one you assumed.

Anything marked `derived` must not enter `data/recipes/` until the licence question in
`OPEN.md` is settled.

## Version comparison (`compare`)

Every prerequisite whose `required` is numeric or parses as a version must explicitly declare `"compare"` as one of `equal`, `exact_major`, or `minimum`. Comparison is never assumed to be a minimum because upstream sources require exact versions in their own words:
- OpenAndroidInstaller (`requirements.android`): *"If your current installation is newer or older than Android 12, please upgrade or downgrade to the required version before proceeding."*
- LineageOS (`spacewar.yml` `before_install`): *"LineageOS builds for this device require an Android 15 version of the stock OS"*.

Treating these as minimums would risk a false safe where a device on a newer version must downgrade before flashing. An undeclared comparison on a version or numeric requirement abstains with `prerequisite-<name>-comparison-undeclared`.
