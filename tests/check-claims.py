#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Check the numbers in the proposal against data/claims.json.

    python3 tests/check-claims.py            fail if a proposal file contradicts a claim
    python3 tests/check-claims.py --final    also recompute live and upstream numbers
    python3 tests/check-claims.py --self-test

A document that NAMES a missing file is caught by check-index.sh. This catches a document
that STATES a wrong number, which is what a reviewer with a GitHub account can check.
"""
import glob
import importlib.util
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
CLAIMS = ROOT / "data" / "claims.json"


def live_metrics():
    spec = importlib.util.spec_from_file_location("cov", ROOT / "data" / "coverage.py")
    cov = importlib.util.module_from_spec(spec)
    sys.argv, saved = [sys.argv[0]], sys.argv
    spec.loader.exec_module(cov)
    sys.argv = saved
    records, _ = cov.load(str(ROOT / "data" / "device-matrix.jsonl"))
    androids = [r for r in records if r.get("detected", {}).get("device_class") in cov.ANDROID_CLASSES]
    complete = set()
    for r in androids:
        a = r["detected"].get("android", {})
        if all(str(a.get(f, "")) not in cov.EMPTY for f in cov.SEVEN):
            complete.add(cov.state_key(a))
    runs = []
    for d in cov.RECIPE_DIRS:
        runs += cov.corpus_runs(d, records)
    paired = cov.distinct([r for r in runs if r.get("paired")])
    decided = sum(1 for r in paired if r["verdict"] in cov.DECIDED)
    fs = sum(1 for r in runs if r["verdict"] == "safe"
             and (r.get("human_assessment") != "safe" or r.get("expected") != "safe"))
    return {"distinct_complete_phones": len(complete),
            "decided_distinct_paired": "%d of %d" % (decided, len(paired)),
            "false_safes": fs}


def check_text(text, name, claims, refused):
    problems = []
    for c in claims:
        for pat in c.get("patterns", []):
            for m in re.finditer(pat, text, re.I):
                got = m.group(1)
                if str(got).replace(",", "") != str(c["value"]):
                    problems.append("%s: says %s for %s, claims.json has %s (as of %s)"
                                    % (name, got, c["id"], c["value"], c["as_of"]))
    for r in refused:
        m = re.search(r["pattern"], text, re.I)
        if m:
            problems.append("%s: refused phrase '%s': %s" % (name, m.group(0), r["why"]))
    return problems


def main():
    data = json.loads(CLAIMS.read_text(encoding="utf-8"))
    claims, refused = data["claims"], data["refused_phrases"]

    if "--self-test" in sys.argv:
        planted = [("OpenAndroidInstaller covers 88 devices.", True),
                   ("About 68% of devices are readable.", True),
                   ("OpenAndroidInstaller covers 90 devices, as of 7 September.", False)]
        for text, should_fail in planted:
            if bool(check_text(text, "plant", claims, refused)) != should_fail:
                print("  check-claims self-test FAILED on: " + text)
                return 1
        print("  check-claims self-test passed")
        return 0

    problems = []
    for rel in data["proposal_files"]:
        p = ROOT / rel
        if p.is_file():
            problems += check_text(p.read_text(encoding="utf-8"), rel, claims, refused)
    for rel in data["historical_files_exempt"]:
        if not re.search(r"\d{4}-\d{2}-\d{2}", rel):
            problems.append("%s is exempt but its name carries no date" % rel)

    if "--final" in sys.argv:
        live = live_metrics()
        for c in claims:
            how = c.get("reproduce", {})
            now = None
            if how.get("kind") == "live":
                now = live[how["metric"]]
            elif how.get("kind") == "count_files":
                files = glob.glob(str(ROOT / how["glob"]))
                now = len(files) if files else None
                if now is None:
                    print("  %-26s upstream clone not present, cannot recount" % c["id"])
                    continue
            else:
                continue
            flag = "" if str(now) == str(c["value"]) else "   MOVED: update claims.json and the text"
            print("  %-26s baseline %-8s now %-8s%s" % (c["id"], c["value"], now, flag))
            if flag:
                problems.append("%s moved from %s to %s" % (c["id"], c["value"], now))

    if problems:
        for p in problems:
            print("  CLAIM: " + p)
        return 1
    print("  proposal numbers agree with data/claims.json (%d claims, %d refused phrases)"
          % (len(claims), len(refused)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
