#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Report what device-matrix.jsonl actually covers. Standard library only."""

import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "device-matrix.jsonl")

ANDROID_CLASSES = {"adb", "fastboot"}


def load(path):
    if not os.path.exists(path):
        sys.exit("no matrix at %s" % path)
    records, bad = [], 0
    with open(path, encoding="utf-8") as fh:
        for n, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                bad += 1
                print("  ! line %d is not valid JSON: %s" % (n, exc), file=sys.stderr)
    return records, bad


def bar(label, count, total, width=28):
    fill = 0 if not total else int(round(width * count / total))
    return "  %-22s %s %d" % (label[:22], "#" * fill + "." * (width - fill), count)


def main():
    records, bad = load(PATH)
    total = len(records)
    if not total:
        print("Matrix is empty. Run the bench protocol and add records.")
        return

    classes = Counter(r.get("detected", {}).get("device_class", "unknown") for r in records)
    androids = [r for r in records if r.get("detected", {}).get("device_class") in ANDROID_CLASSES]

    def android_field(rec, key):
        return rec.get("detected", {}).get("android", {}).get(key, "unknown")

    chipsets = Counter(android_field(r, "board_platform") for r in androids)
    schemes = Counter(android_field(r, "partition_scheme") for r in androids)
    locks = Counter(android_field(r, "bootloader_state") for r in androids)
    testers = Counter(r.get("tester", "?") for r in records)

    runs = [v for r in records for v in r.get("verifier_runs", [])]
    matched = sum(1 for v in runs if v.get("match") is True)
    false_safe = sum(1 for v in runs if v.get("expected") == "unsafe" and v.get("verdict") == "safe")
    abstained = sum(1 for v in runs if v.get("verdict") == "cannot-verify")

    durations = [r.get("duration_minutes") for r in records]
    durations = [d for d in durations if isinstance(d, (int, float))]

    print("\nDEVICE MATRIX COVERAGE")
    print("=" * 52)
    print("  records                %d   (%d testers)" % (total, len(testers)))
    print("  positives (android)    %d" % len(androids))
    print("  negatives              %d" % (total - len(androids)))
    if bad:
        print("  MALFORMED LINES        %d" % bad)

    print("\n  device classes")
    for name, count in classes.most_common():
        print(bar(name, count, total))

    if androids:
        print("\n  chipset families")
        for name, count in chipsets.most_common():
            print(bar(str(name), count, len(androids)))
        print("\n  partition schemes")
        for name, count in schemes.most_common():
            print(bar(str(name), count, len(androids)))
        print("\n  bootloader state")
        for name, count in locks.most_common():
            print(bar(str(name), count, len(androids)))

    print("\n  verifier runs          %d" % len(runs))
    if runs:
        print("  matched expectation    %d / %d" % (matched, len(runs)))
        print("  abstain rate           %.0f%%" % (100.0 * abstained / len(runs)))
        flag = "  <-- BUILD MUST FAIL" if false_safe else ""
        print("  FALSE SAFE             %d%s" % (false_safe, flag))

    if durations:
        print("\n  median minutes/device  %.0f" % sorted(durations)[len(durations) // 2])

    print("\n  gaps to close for the grant")
    if len(androids) < 10:
        print("    - only %d live android positives, target >=10" % len(androids))
    real_chipsets = [c for c in chipsets if c not in ("unknown", "not_applicable")]
    if len(real_chipsets) < 3:
        print("    - only %d chipset families, target >=3" % len(real_chipsets))
    if "A/B" not in schemes or "single" not in schemes:
        print("    - need both A/B and single partition schemes represented")
    print()


if __name__ == "__main__":
    main()
