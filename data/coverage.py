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

    tier_a_gate(records, androids)


SEVEN = ["manufacturer", "product_model", "chipset_family", "android_version",
         "partition_scheme", "bootloader_state", "verified_boot_state"]
EMPTY = ("", None, "unknown", "not_applicable", "not_recorded", "not_saved")


def tier_a_gate(records, androids):
    """Score the dataset against the Tier A exit criterion, field by field.

    Tier A is done when TEN records across at least THREE chipset families
    carry all seven verifier fields, every non-Android device is classified
    correctly against an independently established identity, and no verifier
    run has produced a false safe.
    """
    def fields_present(a):
        return [f for f in SEVEN if str(a.get(f, "")) not in EMPTY]

    complete = [r for r in androids
                if len(fields_present(r.get("detected", {}).get("android", {}))) == len(SEVEN)]
    chips = {r["detected"]["android"].get("chipset_family")
             for r in complete} - set(EMPTY)

    non_android = [r for r in records if r not in androids]
    ground_truth = [r for r in non_android if r.get("identity_source") == "tester_identified"]
    wrong = [r for r in ground_truth if not r.get("classification_correct", False)]
    unverifiable = len(non_android) - len(ground_truth)

    false_safe = sum(1 for r in records for v in r.get("verifier_runs", [])
                     if v.get("expected") == "unsafe" and v.get("verdict") == "safe")

    print("\n  TIER A EXIT CRITERION")
    def row(ok, label, got, want):
        print("    [%s] %-38s %s" % ("x" if ok else " ", label, "%s of %s" % (got, want)))
    row(len(complete) >= 10, "android records with all seven fields", len(complete), 10)
    row(len(chips) >= 3, "distinct chipset families among them", len(chips), 3)
    row(not wrong, "non-android classified correctly", len(ground_truth) - len(wrong), len(ground_truth))
    row(false_safe == 0, "false safes (must be zero)", false_safe, 0)

    if unverifiable:
        print("\n    %d non-android record(s) carry no independent identity, so they" % unverifiable)
        print("    cannot count either way. A record whose identity came from agreeing")
        print("    with the scan cannot be used to validate the scan.")

    if androids and len(complete) < len(androids):
        print("\n  WHICH FIELDS ARE MISSING, ACROSS %d ANDROID RECORD(S)" % len(androids))
        for f in SEVEN:
            n = sum(1 for r in androids
                    if str(r["detected"]["android"].get(f, "")) in EMPTY)
            if n:
                print("    %-22s missing on %d" % (f, n))
        print("\n    A field that is genuinely not exposed by the device is a finding,")
        print("    not a defect. Older hardware often exposes no partition or bootloader")
        print("    property at all, and the verifier has to abstain on exactly those.")
    print()


if __name__ == "__main__":
    main()
