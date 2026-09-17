#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Recipe sanity and producibility check. Run from test suite."""

import json
import os
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]


def get_derive_fields():
    derive_sh = ROOT / "bench-kit" / "scripts" / "derive.sh"
    with open(derive_sh, encoding="utf-8") as f:
        derive_content = f.read()
    return set(re.findall(r"^p\s+([a-zA-Z0-9_]+)", derive_content, re.MULTILINE))


def get_vocabulary():
    vocab_file = ROOT / "data" / "vocabulary.json"
    with open(vocab_file, encoding="utf-8") as f:
        return json.load(f)


def check_schema_table_agrees_with_vocabulary(vocab):
    schema_md = ROOT / "data" / "schema.md"
    with open(schema_md, encoding="utf-8") as f:
        content = f.read()

    # Check operation kinds in schema.md
    for kind in vocab.get("operation_kinds", {}).keys():
        if f"`{kind}`" not in content:
            raise AssertionError(f"data/schema.md missing operation kind `{kind}` from vocabulary.json")

    # Check unlock classes
    for uc in vocab.get("unlock_classes", []):
        if f"`{uc}`" not in content and uc not in content:
            raise AssertionError(f"data/schema.md missing unlock class `{uc}` from vocabulary.json")

    # Check unlock evidence fields
    for uef in vocab.get("unlock_evidence_fields", {}).keys():
        if f"`{uef}`" not in content and uef not in content:
            raise AssertionError(f"data/schema.md missing unlock evidence field `{uef}` from vocabulary.json")

    # Check refused names
    for k, v in vocab.get("refused_prerequisite_names", {}).items():
        if f"`{k}`" not in content or f"`{v}`" not in content:
            raise AssertionError(f"data/schema.md missing refused name `{k}` -> `{v}` from vocabulary.json")

    # Check comparisons
    for comp in vocab.get("prerequisite_comparisons", []):
        if f"`{comp}`" not in content and comp not in content:
            raise AssertionError(f"data/schema.md missing comparison `{comp}` from vocabulary.json")


def check_recipe(recipe, recipe_name, derive_fields, vocab):
    refused = vocab.get("refused_prerequisite_names", {})
    unlock_evidence_fields = vocab.get("unlock_evidence_fields", {})
    prerequisites = recipe.get("prerequisites") or {}
    for prereq_name, req in prerequisites.items():
        if prereq_name in refused:
            replacement = refused[prereq_name]
            raise AssertionError(
                f"Recipe '{recipe_name}' uses refused prerequisite name '{prereq_name}', use '{replacement}' instead."
            )
        if prereq_name not in derive_fields:
            raise AssertionError(
                f"Recipe '{recipe_name}' prerequisite '{prereq_name}' requires evidence field "
                f"'{prereq_name}' which is produced by no capture route."
            )
        if isinstance(req, dict) and req.get("unlock_class"):
            if prereq_name not in unlock_evidence_fields:
                raise AssertionError(
                    f"Recipe '{recipe_name}' prerequisite '{prereq_name}' carries unlock_class but is not an unlock evidence field."
                )


def main():
    derive_fields = get_derive_fields()
    vocab = get_vocabulary()
    check_schema_table_agrees_with_vocabulary(vocab)

    errors = []
    recipe_dirs = [ROOT / "data" / "recipes", ROOT / "data" / "recipes-v0.2"]
    for recipe_dir in recipe_dirs:
        if not recipe_dir.is_dir():
            continue
        for recipe_path in sorted(recipe_dir.glob("*.json")):
            with open(recipe_path, encoding="utf-8") as fh:
                recipe = json.load(fh)
            try:
                check_recipe(recipe, recipe_path.name, derive_fields, vocab)
            except AssertionError as exc:
                errors.append(str(exc))

    if errors:
        for err in errors:
            print(f"  ERROR: {err}", file=sys.stderr)
        sys.exit(1)

    print("  all recipes validated against vocabulary and derived fields")


if __name__ == "__main__":
    main()
