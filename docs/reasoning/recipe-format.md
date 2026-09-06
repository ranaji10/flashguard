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
    "variant": "global",
    "partition_scheme": "A/B"
  },
  "assets": [
    {
      "asset_id": "system",
      "role": "system",
      "product_device": "oriole",
      "variant": "global"
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
`target` requires `product_device`, `variant`, and `partition_scheme`. Each asset
requires `asset_id`, `role`, `product_device`, and `variant`; asset IDs are unique.
Each operation requires `kind`, `partition`, and `asset_id`, and its asset ID must
refer to an entry in `assets`. Operation order is significant.

Corpus recipes also carry `expected_verdict` and `expected_verdict_reason`. These
are human-established labels, not verifier output. `expected_verdict` is one of
`safe`, `unsafe`, or `cannot-verify`; the reason records the evidence and why the
label was assigned. A recipe with an incomplete translation of a source procedure
must not receive `safe` merely because the omitted steps are absent from its own
operations.

Version 0.1 supports only the declarative `write-image` operation. It names a
partition and an already-identified asset; it contains no shell, fastboot, adb, or
filesystem command. Unknown operation kinds are outside the model and therefore
produce `cannot-verify`, rather than being guessed at.

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
  "verdict_reason": "why a human assigned this verdict"
}
```

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
