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

    # Check unlock evidence fields: assert the table row itself contains unlock_evidence_fields, `bootloader_state` and `unlocked`
    for uef, uval in vocab.get("unlock_evidence_fields", {}).items():
        found = False
        for line in content.splitlines():
            if "unlock_evidence_fields" in line and f"`{uef}`" in line and f"`{uval}`" in line:
                found = True
                break
        if not found:
            raise AssertionError(
                f"data/schema.md missing table row containing `unlock_evidence_fields`, `{uef}` and `{uval}`"
            )

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
            expected_val = unlock_evidence_fields[prereq_name]
            if req.get("required") != expected_val:
                raise AssertionError(
                    f"Recipe '{recipe_name}' prerequisite '{prereq_name}' carries unlock_class but requires '{req.get('required')}' instead of '{expected_val}'."
                )


def self_test():
    derive_fields = get_derive_fields()
    vocab = get_vocabulary()

    # Plant 1: unlock_class on android_version
    plant1 = {
        "prerequisites": {
            "android_version": {
                "state": "OPEN",
                "required": "15",
                "compare": "exact_major",
                "unlock_class": "command",
            }
        }
    }
    p1_failed = False
    try:
        check_recipe(plant1, "plant1.json", derive_fields, vocab)
    except AssertionError:
        p1_failed = True

    # Plant 2: bootloader_state required locked with unlock_class
    plant2 = {
        "prerequisites": {
            "bootloader_state": {
                "state": "OPEN",
                "required": "locked",
                "unlock_class": "command",
            }
        }
    }
    p2_failed = False
    try:
        check_recipe(plant2, "plant2.json", derive_fields, vocab)
    except AssertionError:
        p2_failed = True

    if not (p1_failed and p2_failed):
        print("  ERROR: check-recipes self-test failed: expected planted defects to raise AssertionError", file=sys.stderr)
        sys.exit(1)
    print("  check-recipes self-test passed")
    sys.exit(0)


def main():
    if "--self-test" in sys.argv:
        self_test()

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
