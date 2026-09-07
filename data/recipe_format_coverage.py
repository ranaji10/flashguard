#!/usr/bin/env python3
"""Measure v0.1 recipe-field coverage in the cloned upstream sources."""

import json
import os
import re
import subprocess
import sys

from prerequisite_survey import survey_text


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
UPSTREAM = os.path.abspath(os.path.join(ROOT, "..", "library", "upstream"))


def checkout_hash(path):
    return subprocess.check_output(["git", "-C", path, "rev-parse", "HEAD"], text=True).strip()


def active_oai():
    root = os.path.join(UPSTREAM, "openandroidinstaller", "openandroidinstaller", "assets", "configs")
    return [(path, "openandroidinstaller") for name in sorted(os.listdir(root))
            if name.endswith(".yaml")
            for path in [os.path.join(root, name)]]


def all_files(root, suffix=None, basename=None):
    for directory, _, names in os.walk(root):
        for name in sorted(names):
            if suffix and not name.endswith(suffix):
                continue
            if basename and name != basename:
                continue
            yield os.path.join(directory, name)


def sources():
    return {
        "OpenAndroidInstaller": active_oai(),
        "postmarketOS": [(path, "postmarketos") for path in all_files(
            os.path.join(UPSTREAM, "pmaports"), basename="deviceinfo")],
        "LineageOS": [(path, "lineage_metadata") for path in all_files(
            os.path.join(UPSTREAM, "lineage_wiki", "_data", "devices"), ".yml")],
    }


def has(text, pattern):
    return re.search(pattern, text, re.MULTILINE) is not None


def facts(text, source):
    evidence = survey_text(text, source)
    if source == "openandroidinstaller":
        variant = has(text, r"^\s*(supported_device_codes|variant):")
        assets = has(text, r"^\s*(assets|payload|image_file):")
        operations = has(text, r"^steps:")
        partitions = has(text, r"^\s*additional_steps:")
    elif source == "postmarketos":
        variant = has(text, r"^deviceinfo_variant=")
        assets = False
        operations = has(text, r"^deviceinfo_flash_method=|^deviceinfo_.*partition=")
        partitions = has(text, r"^deviceinfo_(partition_type|super_partitions)=")
    else:
        variant = has(text, r"^variant:")
        assets = False
        operations = has(text, r"^(install_method|before_install|before_recovery_install):")
        partitions = has(text, r"^before_recovery_install:")
    return {
        "schema_version": True,
        "recipe_id": True,
        "source.device_facts_from": True,
        "source.consulted": False,
        "source.authored": False,
        "source.verdict_reason": False,
        "human_assessment": False,
        "expected_verdict": False,
        "expected_verdict_reason": False,
        "verdict_gap_reason": False,
        "target.product_device": evidence["identity"] == "structured",
        "target.variant": variant,
        "target.partition_scheme": evidence["partition_scheme"] == "structured",
        "assets": assets,
        "assets.asset_id": assets,
        "assets.role": assets,
        "assets.product_device": evidence["identity"] == "structured" and assets,
        "assets.variant": variant and assets,
        "operations": operations,
        "operations.kind": operations,
        "operations.partition": partitions,
        "operations.asset_id": False,
    }


def main():
    result = {"commits": {
        "OpenAndroidInstaller": checkout_hash(os.path.join(UPSTREAM, "openandroidinstaller")),
        "postmarketOS": checkout_hash(os.path.join(UPSTREAM, "pmaports")),
        "LineageOS": checkout_hash(os.path.join(UPSTREAM, "lineage_wiki")),
    }, "projects": {}}
    for project, paths in sources().items():
        counts = {}
        for path, source in paths:
            with open(path, encoding="utf-8") as handle:
                record = facts(handle.read(), source)
            for field, present in record.items():
                counts.setdefault(field, 0)
                counts[field] += int(present)
        denominator = len(paths)
        result["projects"][project] = {
            "denominator": denominator,
            "counts": counts,
        }
    json.dump(result, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()