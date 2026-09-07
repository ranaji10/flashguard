#!/usr/bin/env python3
"""Survey cloned upstream sources without copying their contents into project."""

import json
import os
import sys
from collections import Counter

from prerequisite_survey import survey_text


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
UPSTREAM = os.path.abspath(os.path.join(ROOT, "..", "library", "upstream"))


def files(root, suffix=None, basename=None):
    for directory, _, names in os.walk(root):
        for name in sorted(names):
            if suffix and not name.endswith(suffix):
                continue
            if basename and name != basename:
                continue
            yield os.path.join(directory, name)


def root_files(root, suffix):
    for name in sorted(os.listdir(root)):
        path = os.path.join(root, name)
        if os.path.isfile(path) and name.endswith(suffix):
            yield path


def count_source(paths, source):
    counts = {field: Counter() for field in ("unlock", "partition_scheme", "identity")}
    total = 0
    for path in paths:
        with open(path, encoding="utf-8") as handle:
            result = survey_text(handle.read(), source)
        total += 1
        for field, value in result.items():
            counts[field][value] += 1
    return {"denominator": total, "counts": {field: dict(value) for field, value in counts.items()}}


def main():
    result = {
        "openandroidinstaller": count_source(
            root_files(os.path.join(UPSTREAM, "openandroidinstaller", "openandroidinstaller", "assets", "configs"), ".yaml"),
            "openandroidinstaller",
        ),
        "postmarketos": count_source(
            files(os.path.join(UPSTREAM, "pmaports"), basename="deviceinfo"),
            "postmarketos",
        ),
        "lineage_metadata": count_source(
            files(os.path.join(UPSTREAM, "lineage_wiki", "_data", "devices"), ".yml"),
            "lineage_metadata",
        ),
        "lineage_install_pages": {
            "denominator": sum(1 for _ in files(os.path.join(UPSTREAM, "lineage_wiki", "pages", "install"), ".md")),
            "mechanically_surveyable": False,
            "reason": "Pages are template-backed wiki prose; rendering the includes is outside this text-only survey.",
        },
    }
    json.dump(result, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()