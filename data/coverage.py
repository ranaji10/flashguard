#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Report what device-matrix.jsonl actually covers. Standard library only."""

import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "device-matrix.jsonl")
RECIPE_DIRS = (os.path.join(HERE, "recipes"), os.path.join(HERE, "recipes-v0.2"))
FLOOR_PATH = os.path.join(HERE, "coverage-floor.json")
ROOT = os.path.dirname(HERE)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from flashguard import verify
from flashguard.reasons import kind_label

DECIDED = ("safe", "not-ready", "unsafe")
# Fields that describe the phone's state as the verifier sees it. Two captures with the
# same values here are the same observation: re-reading an unchanged phone adds nothing.
# Two different phones of the same model on the same firmware would also collapse into one,
# which undercounts. That is the conservative direction.
STATE_KEY_FIELDS = ("product_device", "product_model", "build_fingerprint", "security_patch",
                    "android_version", "partition_scheme", "bootloader_state", "verified_boot_state")
UPSTREAM = os.path.join(os.path.dirname(ROOT), "library", "upstream")

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


def load_coverage_floor():
    if os.path.exists(FLOOR_PATH):
        try:
            with open(FLOOR_PATH, encoding="utf-8") as fh:
                return json.load(fh)
        except Exception:
            return None
    return None


def get_android_facts(record):
    """Extract and return the android facts dictionary from a record."""
    detected = record.get("detected") or {}
    android = detected.get("android") or {}
    return dict(android)


def state_key(android):
    """The observation a capture represents, ignoring USB mode, tester and date."""
    return tuple(str(android.get(f, "")) for f in STATE_KEY_FIELDS)


def match_recipe_target(product_device, recipe):
    """Return True if product_device matches target.product_device or supported_device_codes."""
    target = recipe.get("target") or {}
    target_device = (target.get("product_device") or "").lower()
    target_aliases = [code.lower() for code in target.get("supported_device_codes", [])]
    device_lower = (product_device or "").lower()
    if not device_lower or device_lower == "not_applicable":
        return False
    return device_lower == target_device or device_lower in target_aliases


def load_all_recipes(recipe_dirs=RECIPE_DIRS):
    """Load all recipe JSON files from the provided directories."""
    recipes = []
    for rdir in recipe_dirs:
        if not os.path.isdir(rdir):
            continue
        for name in sorted(os.listdir(rdir)):
            if not name.endswith(".json"):
                continue
            path = os.path.join(rdir, name)
            with open(path, encoding="utf-8") as fh:
                try:
                    data = json.load(fh)
                    recipes.append((name, data))
                except Exception:
                    pass
    return recipes


def pair_record_with_recipes(record, recipes):
    """Return list of (recipe_name, recipe_dict) that pair with this record."""
    android = get_android_facts(record)
    product_device = android.get("product_device")
    paired = []
    for rname, recipe in recipes:
        if match_recipe_target(product_device, recipe):
            paired.append((rname, recipe))
    return paired


def corpus_runs(recipe_dir, records):
    runs = []
    if not os.path.isdir(recipe_dir):
        return runs
    for name in sorted(os.listdir(recipe_dir)):
        if not name.endswith(".json"):
            continue
        path = os.path.join(recipe_dir, name)
        with open(path, encoding="utf-8") as fh:
            recipe = json.load(fh)

        matching_records = []
        for r in records:
            android = get_android_facts(r)
            device = android.get("product_device")
            if match_recipe_target(device, recipe):
                matching_records.append(r)

        if matching_records:
            for r in matching_records:
                android = get_android_facts(r)
                result = verify(android, recipe)
                runs.append({
                    "recipe_id": recipe.get("recipe_id", name),
                    "human_assessment": recipe.get("human_assessment"),
                    "expected": recipe.get("expected_verdict"),
                    "verdict": result.get("verdict"),
                    "paired": True,
                    "fingerprint_source": r.get("record_id") or r.get("device_local_id"),
                    "observation": (recipe.get("recipe_id", name),) + state_key(android),
                    "reasons": [(x.get("code"), x.get("result"), x.get("kind"), x.get("plain"))
                                for x in result.get("reasons", [])],
                })
        else:
            result = verify({}, recipe)
            runs.append({
                "recipe_id": recipe.get("recipe_id", name),
                "human_assessment": recipe.get("human_assessment"),
                "expected": recipe.get("expected_verdict"),
                "verdict": result.get("verdict"),
                "paired": False,
                "fingerprint_source": None,
                "observation": (recipe.get("recipe_id", name), "no-device"),
                "reasons": [(x.get("code"), x.get("result"), x.get("kind"), x.get("plain"))
                            for x in result.get("reasons", [])],
            })
    return runs


def distinct(runs):
    """One run per observation. Runs without an observation key count individually."""
    seen, out = set(), []
    for run in runs:
        key = run.get("observation")
        if key is None:
            out.append(run)
            continue
        if key in seen:
            continue
        seen.add(key)
        out.append(run)
    return out


def abstention_kind(run):
    """For a cannot-verify run: 'our_gap' if any abstention is ours to fix, else 'honest'."""
    kinds = [k for (_c, result, k, _p) in run.get("reasons", []) if result == "abstain"]
    if any(k == "our_gap" for k in kinds):
        return "our_gap"
    if any(k == "unclassified" for k in kinds):
        return "unclassified"
    return "honest"


def enforce_false_safe_gate(runs):
    false_safe = sum(
        1 for run in runs
        if run.get("verdict") == "safe" and (run.get("human_assessment") != "safe" or run.get("expected") != "safe")
    )
    if false_safe:
        print("    FALSE SAFE: %d -- BUILD MUST FAIL" % false_safe)
        raise SystemExit(1)


def enforce_verifier_gate(runs, floor_data=None):
    enforce_false_safe_gate(runs)
    if floor_data is None:
        floor_data = load_coverage_floor()
    floor = floor_data.get("decided_over_paired") if floor_data else None
    paired_runs = distinct([v for v in runs if v.get("paired")])
    decided = sum(1 for v in paired_runs if v.get("verdict") in DECIDED)
    share = (decided / len(paired_runs)) if paired_runs else 0.0
    if floor is not None and share < floor:
        print("    DECIDED SHARE BELOW FLOOR: %.2f < %.2f -- BUILD MUST FAIL" % (share, floor))
        raise SystemExit(1)


corpus_runs_cache = {}


def report_corpus_runs(records):
    print("  CORPUS REPLAY")
    all_runs = []
    for label, recipe_dir in (("v0.1", RECIPE_DIRS[0]), ("v0.2", RECIPE_DIRS[1])):
        runs = corpus_runs(recipe_dir, records)
        corpus_runs_cache[label] = runs
        all_runs.extend(runs)
        print("    %s" % label)
        if not runs:
            print("      no recipe files")
            continue
        report_corpus_group(runs)
    enforce_false_safe_gate(all_runs)
    print("    These are format fixtures, not hardware validation.")
    print()
    v02_runs = [r for r in all_runs if r in corpus_runs_cache.get("v0.2", [])]
    report_abstentions(v02_runs)
    report_unpaired_devices(records, load_all_recipes())
    return all_runs


def report_corpus_group(runs):
    obs = distinct(runs)
    counts = Counter(run["verdict"] for run in obs)
    false_safe = sum(
        1 for run in runs
        if run.get("verdict") == "safe" and (run.get("human_assessment") != "safe" or run.get("expected") != "safe")
    )
    decided = sum(1 for run in obs if run["verdict"] in DECIDED)
    definite_human = sum(1 for run in obs if run["human_assessment"] in ("safe", "unsafe"))
    information_loss = sum(1 for run in obs
                           if run["human_assessment"] in ("safe", "unsafe")
                           and run["expected"] not in ("safe", "unsafe"))
    distinct_recipes = len(set(run["recipe_id"] for run in runs))
    total = len(obs)
    print("      recipes                 %d" % distinct_recipes)
    print("      runs                    %d  (%d distinct: a phone read again unchanged counts once)" % (len(runs), total))
    print("      safe                    %d" % counts.get("safe", 0))
    print("      not-ready               %d   right recipe, phone not ready yet" % counts.get("not-ready", 0))
    print("      unsafe                  %d   wrong recipe for this phone" % counts.get("unsafe", 0))
    print("      cannot-verify           %d" % counts.get("cannot-verify", 0))
    print("      false safes             %d  (over all %d runs)" % (false_safe, len(runs)))
    print("      decided                 %d / %d distinct (%.0f%%)" %
          (decided, total, 100.0 * decided / total if total else 0))
    print("      information loss        %d / %d definite human assessments (%.0f%%)" %
          (information_loss, definite_human,
           100.0 * information_loss / definite_human if definite_human else 0))
    paired = sum(1 for run in obs if run.get("paired"))
    print("      paired                  %d / %d distinct" % (paired, total))
    if paired < total:
        print("      decided cannot exceed paired: a recipe with no captured device has no")
        print("      evidence to check against, so it abstains. That is a gap in the matrix,")
        print("      not in the verifier, and it closes by capturing devices.")


def report_abstentions(runs):
    """Split every cannot-verify into honest abstentions and gaps that are ours to fix."""
    held = [r for r in distinct(runs) if r["verdict"] == "cannot-verify"]
    unpaired = [r for r in held if not r.get("paired")]
    obs = [r for r in held if r.get("paired")]
    print("  WHY THE VERIFIER HELD BACK (%d distinct cannot-verify)" % len(held))
    if unpaired:
        print("    %-3d No phone has been captured for this recipe yet, so there is nothing to check." % len(unpaired))
    if not obs:
        print("    nothing held back")
        print()
        return
    by_kind = Counter(abstention_kind(r) for r in obs)
    for kind in ("honest", "our_gap", "unclassified"):
        if by_kind.get(kind):
            print("    %-3d %s" % (by_kind[kind], kind_label(kind)))
    reasons = Counter()
    plain = {}
    for r in obs:
        for code, result, kind, text in r.get("reasons", []):
            if result in ("abstain", "unmet"):
                reasons[(kind, code)] += 1
                plain[code] = text
    print()
    for (kind, code), n in sorted(reasons.items(), key=lambda kv: (kv[0][0] != "honest", -kv[1])):
        tag = {"honest": "honest ", "our_gap": "our gap", "not_ready": "unmet  "}.get(kind, kind[:7])
        print("    [%s] %-2d %s" % (tag, n, plain[code]))
        print("               %s" % code)
    print()


def report_unpaired_devices(records, recipes, upstream=None):
    """Captured Android phones with no recipe, and whether upstream covers them."""
    upstream = UPSTREAM if upstream is None else upstream
    lineage = os.path.join(upstream, "lineage_wiki", "_data", "devices")
    oai = os.path.join(upstream, "openandroidinstaller", "openandroidinstaller", "assets", "configs")
    have_upstream = os.path.isdir(lineage) or os.path.isdir(oai)
    missing = {}
    for r in records:
        android = get_android_facts(r)
        dev = android.get("product_device")
        if not dev or dev in ("unknown", "not_applicable"):
            continue
        if not pair_record_with_recipes(r, recipes):
            missing.setdefault(dev, android.get("product_model") or "?")
    out = []
    print("  CAPTURED PHONES WITH NO RECIPE")
    if not missing:
        print("    none: every captured Android codename has a recipe")
    for dev, model in sorted(missing.items()):
        where = []
        if os.path.isfile(os.path.join(lineage, dev + ".yml")):
            where.append("LineageOS")
        if os.path.isfile(os.path.join(oai, dev + ".yaml")):
            where.append("OpenAndroidInstaller")
        if where:
            note = "covered upstream by " + " and ".join(where) + ": write the recipe"
        elif have_upstream:
            note = "no upstream recipe: record that as a finding"
        else:
            note = "upstream clones not found, cannot check"
        out.append((dev, model, note))
        print("    %-16s %-14s %s" % (dev, model, note))
    print()
    return out


SEVEN = ["manufacturer", "product_model", "chipset_family", "android_version",
         "partition_scheme", "bootloader_state", "verified_boot_state"]
EMPTY = ("", None, "unknown", "not_applicable", "not_recorded", "not_saved")


def tier_a_gate(records, androids, all_runs):
    """Score the dataset against the Tier A exit criterion, field by field.

    Tier A is done when TEN records across at least THREE chipset families
    carry all seven verifier fields, every non-Android device is classified
    correctly against an independently established identity, and no verifier
    run has produced a false safe.
    """
    def fields_present(a):
        return [f for f in SEVEN if str(a.get(f, "")) not in EMPTY]

    complete_all = [r for r in androids
                    if len(fields_present(r.get("detected", {}).get("android", {}))) == len(SEVEN)]
    # One phone read several times without changing counts once.
    complete, seen = [], set()
    for r in complete_all:
        key = state_key(r["detected"]["android"])
        if key not in seen:
            seen.add(key)
            complete.append(r)
    chips = {r["detected"]["android"].get("chipset_family")
             for r in complete} - set(EMPTY)

    non_android = [r for r in records if r not in androids]
    ground_truth = [r for r in non_android if r.get("identity_source") == "tester_identified"]
    wrong = [r for r in ground_truth if not r.get("classification_correct", False)]
    unverifiable = len(non_android) - len(ground_truth)

    false_safe = sum(
        1 for v in all_runs
        if v.get("verdict") == "safe" and (v.get("human_assessment") != "safe" or v.get("expected") != "safe")
    )

    print("\n  TIER A EXIT CRITERION")
    def row(ok, label, got, want):
        print("    [%s] %-38s %s" % ("x" if ok else " ", label, "%s of %s" % (got, want)))
    row(len(complete) >= 10, "distinct phones with all seven fields", len(complete), 10)
    if len(complete_all) > len(complete):
        print("        (%d records; repeat reads of an unchanged phone count once)" % len(complete_all))
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


def verifier_gate(runs):
    """The paired gate: zero false safes AND a minimum share actually decided.

    Reported together, always, so 'zero false safes' can never be read as
    'it refuses everything'. See docs/reasoning/verifier-plan.md.
    """
    print("  VERIFIER GATE")
    false_safe = sum(
        1 for v in runs
        if v.get("verdict") == "safe" and (v.get("human_assessment") != "safe" or v.get("expected") != "safe")
    )
    paired_runs = distinct([v for v in runs if v.get("paired")])
    decided = sum(1 for v in paired_runs if v.get("verdict") in DECIDED)
    share = (decided / len(paired_runs)) if paired_runs else 0.0

    floor_data = load_coverage_floor()
    floor = floor_data.get("decided_over_paired") if floor_data else None

    ok_fs = false_safe == 0
    print("    [%s] false safes == 0                     %d of %d runs"
          % ("x" if ok_fs else " ", false_safe, len(runs)))
    if floor is None:
        print("    [ ] decided share over paired >= floor    %.0f%% decided, NO FLOOR SET" %
              (100 * share))
    else:
        ok_ds = share >= floor
        print("    [%s] decided share over paired >= %.0f%%       %.0f%% decided (%d of %d distinct paired)"
              % ("x" if ok_ds else " ", 100 * floor, 100 * share, decided, len(paired_runs)))
        if not ok_ds:
            print("    DECIDED SHARE BELOW FLOOR: %.2f < %.2f -- BUILD MUST FAIL" % (share, floor))
            raise SystemExit(1)
    if not ok_fs:
        print("\n    A FALSE SAFE FAILS THE BUILD. It is the one unacceptable error.")
        raise SystemExit(1)
    print()


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
    routes = Counter(r.get("capture_route", "linux_live") for r in records)
    testers = Counter(r.get("tester", "?") for r in records)

    durations = [r.get("duration_minutes") for r in records]
    durations = [d for d in durations if isinstance(d, (int, float))]

    print("\nDEVICE MATRIX COVERAGE")
    print("=" * 52)
    print("  records                %d   (%d testers)" % (total, len(testers)))
    print("  positives (android)    %d" % len(androids))
    print("  negatives              %d" % (total - len(androids)))
    if bad:
        print("  MALFORMED LINES        %d" % bad)

    print("\n  capture routes")
    for name, count in routes.most_common():
        print(bar(name, count, total))

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

    if durations:
        print("\n  median minutes/device  %.0f" % sorted(durations)[len(durations) // 2])

    all_runs = report_corpus_runs(records)
    tier_a_gate(records, androids, all_runs)
    verifier_gate(all_runs)


if __name__ == "__main__":
    main()
