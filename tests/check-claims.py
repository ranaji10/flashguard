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
    # A pending not-ready waits on a person and is not decided (ruled 8 October 2026),
    # the same rule data/coverage.py applies in its gate.
    decided = sum(1 for r in paired if r["verdict"] in cov.DECIDED
                  and not r.get("pending_confirmation"))
    fs = sum(1 for r in runs if r["verdict"] == "safe"
             and (r.get("human_assessment") != "safe" or r.get("expected") != "safe"))

    # Matrix figures quoted in README.md and the proposal (added 24 October 2026, when the
    # README's "Fifteen volunteers, 40 phones, 24 of 24" had gone stale with nothing to catch it).
    # A phone is a distinct model as read: same codename and same board. Two Ubuntu Touch
    # phones both report the codename halium_arm64, so the codename alone undercounts.
    phones = {}
    for r in androids:
        a = r["detected"].get("android", {})
        if str(a.get("android_version", "")) in cov.EMPTY:
            continue
        phones.setdefault((a.get("product_device"), a.get("board_platform")), []).append(a)

    def sdk(a):
        try:
            return int(a.get("sdk"))
        except (TypeError, ValueError):
            return None

    def lock_read(reads):
        return any(str(a.get("bootloader_state", "")) not in cov.EMPTY for a in reads)
    newer = [v for v in phones.values() if (sdk(v[-1]) or 0) >= 26]
    older = [v for v in phones.values() if sdk(v[-1]) is not None and sdk(v[-1]) < 26]
    ab = [v for v in phones.values()
          if any(a.get("partition_scheme") in cov.LAYOUTS_REPORTED_AB for a in v)]
    six = [f for f in cov.SEVEN if f != "partition_scheme"]
    unreported = {cov.state_key(r["detected"]["android"]) for r in androids
                  if str(r["detected"]["android"].get("partition_scheme", "")) in cov.EMPTY
                  and all(str(r["detected"]["android"].get(f, "")) not in cov.EMPTY for f in six)}
    return {"distinct_complete_phones": len(complete),
            "decided_distinct_paired": "%d of %d" % (decided, len(paired)),
            "false_safes": fs,
            "matrix_records": len(records),
            "testers": len({r.get("tester") for r in records}),
            "distinct_android_phones": len(phones),
            "lock_read_android8": "%d of %d" % (sum(lock_read(v) for v in newer), len(newer)),
            "lock_read_older": "%d of %d" % (sum(lock_read(v) for v in older), len(older)),
            "ab_reported_phones": len(ab),
            "complete_layout_unreported": len(unreported)}


# Prose spells small numbers out ("Fifteen volunteers"). Compare them as digits.
WORDS = {w: str(i) for i, w in enumerate(
    "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen "
    "fifteen sixteen seventeen eighteen nineteen twenty".split())}


def check_text(text, name, claims, refused):
    problems = []
    # A number wrapped onto the next line ("decided\n  on 2 of 7") slipped past every pattern
    # until 24 October 2026, and grant/schedule.md quoted an 11 October figure unnoticed.
    text = re.sub(r"\s+", " ", text)
    for c in claims:
        for pat in c.get("patterns", []):
            for m in re.finditer(pat, text, re.I):
                got = WORDS.get(m.group(1).lower(), m.group(1))
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
                   ("0 false safes across 24 runs, decided\n  on 2 of 7 distinct pairings.", True),
                   ("Fourteen volunteers have read 40 distinct Android phones.", True),
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
