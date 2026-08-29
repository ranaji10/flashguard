#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""
Turn captured USB descriptors into test fixtures with real ground truth.

    python3 tests/promote.py            report what would change
    python3 tests/promote.py --write    stamp the headers

A descriptor arrives from 01-detect.sh with `#!expect=` set to whatever the
CLASSIFIER guessed. That is worthless as a test: it freezes today's answer as
tomorrow's requirement, whether or not it was right.

This walks the matrix and, for every record where a HUMAN named the device before
the scan ran (identity_source == tester_identified) and confirmed the result
(classification_correct), rewrites that descriptor's `#!expect` from the record's
class and stamps where the expectation came from. A record that fails either test
is left alone and reported: the descriptor stays in the folder as evidence but
never becomes an assertion.

This is the step that converts a tester's evening into a permanent regression
test. Fifteen testers returning descriptors gives a suite that keeps checking the
classifier long after their devices are gone.
"""
import json, pathlib, sys

# Verdicts that mean "I could not tell". None of these can be an expectation.
ABSTENTIONS = {"unknown", "ptp_or_mtp", "not_detected", "cdc_other"}

HERE = pathlib.Path(__file__).parent
MATRIX = HERE.parent / "data" / "device-matrix.jsonl"
DESCDIR = HERE / "real-descriptors"

def main():
    write = "--write" in sys.argv
    if not MATRIX.exists():
        sys.exit(f"no matrix at {MATRIX}")
    records = [json.loads(l) for l in MATRIX.read_text().splitlines() if l.strip()]
    promoted, skipped, missing = [], [], []

    for r in records:
        fn = r.get("descriptor_file")
        if not fn or fn in ("not_saved", "not_applicable"):
            continue
        path = DESCDIR / fn
        if not path.exists():
            missing.append(fn); continue
        cls = r["detected"]["device_class"]
        why = None
        if r.get("identity_source") != "tester_identified":
            why = "identity_source is not tester_identified"
        elif not r.get("classification_correct"):
            why = "the tester corrected the classification; set #!expect by hand"
        elif cls in ABSTENTIONS:
            # "classification_correct" on an abstention means the tester agreed the
            # tool could not tell -- NOT that "unknown" is the device's true class.
            # Promoting it would freeze an abstention as a requirement and block the
            # classifier from ever improving on that device.
            why = f"'{cls}' is an abstention, not an identity; it cannot be ground truth"
        if why:
            skipped.append((fn, why)); continue

        body = [l for l in path.read_text().splitlines()
                if not l.startswith(("#!expect=", "#!ground_truth=", "#!device=",
                                     "#!tester=", "#!promoted"))]
        head = [
            f"#!expect={cls}",
            "#!ground_truth=tester_identified",
            f"#!device={r.get('reported_device','?')}",
            f"#!tester={r.get('tester','?')}",
            "#!promoted=named by a human BEFORE the scan ran, and confirmed after",
        ]
        new = "\n".join(head + body) + "\n"
        if write and new != path.read_text():
            path.write_text(new)
        promoted.append((fn, cls, r.get("reported_device")))

    print(f"\n  {len(promoted)} descriptor(s) carry real ground truth"
          + ("" if write else "  (dry run, pass --write)"))
    for fn, cls, dev in promoted:
        print(f"    {fn:<34} {cls:<14} {dev}")
    if skipped:
        print(f"\n  {len(skipped)} left as evidence only, not as assertions")
        for fn, why in skipped:
            print(f"    {fn:<34} {why}")
    if missing:
        print(f"\n  {len(missing)} descriptor named on a record but not in "
              f"{DESCDIR.name}/ -- copy them off the stick")
        for fn in missing:
            print(f"    {fn}")
    print()

if __name__ == "__main__":
    main()
