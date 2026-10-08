#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Record a person's answer to a verifier's model question.

Ruled 8 Oct 2026 (revised the same day): capture asks the tester nothing about the model.
The verifier settles the model from credible public sources. Only when no credible source
lists a model code does it return a confirmation_request: the models the phone reports,
the links the recipe rests on, and the upstream entries it cannot tell apart. This tool
records the answer for a phone already in the matrix, into data/confirmations.jsonl,
which merge.py applies. A tester's own file is never edited.

Usage:
    python3 tools/confirm-model.py --pending                 # questions the verifier is asking now
    python3 tools/confirm-model.py --record-id <uuid> --source <link they recognised> --by <handle>
    python3 tools/confirm-model.py --record-id <uuid> --rejected --by <handle>
"""
import argparse
import datetime
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MATRIX = ROOT / "data" / "device-matrix.jsonl"
DEFAULT_OUT = ROOT / "data" / "confirmations.jsonl"


def load_matrix(path):
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def pending(records):
    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(ROOT / "data"))
    from flashguard import verify
    import coverage
    recipes = coverage.load_all_recipes([ROOT / "data" / "recipes-v0.2"])
    for r in records:
        for name, recipe in coverage.pair_record_with_recipes(r, recipes):
            res = verify(coverage.get_android_facts(r), recipe)
            req = (res.get("evidence") or {}).get("confirmation_request")
            if not req:
                continue
            print("%s  %s / %s  recipe %s" % (r.get("record_id"), r.get("tester"), r.get("device_local_id"), recipe.get("recipe_id", name)))
            print("    " + req["question"])
            for s in req["recipe_sources"]:
                print("      this recipe:  %s  %s" % (s.get("project", ""), s.get("url", "")))
            for s in req["cannot_tell_apart_from"]:
                print("      not this one: %s  %s  %s" % (s.get("project", ""), s.get("name", ""), s.get("url", "")))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--record-id")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--source", help="the link the person recognised as their phone")
    g.add_argument("--rejected", action="store_true", help="the person said it is not that device")
    ap.add_argument("--by", help="handle of the person holding the phone")
    ap.add_argument("--pending", action="store_true")
    ap.add_argument("--matrix", default=str(MATRIX), help=argparse.SUPPRESS)
    ap.add_argument("--out", default=str(DEFAULT_OUT), help=argparse.SUPPRESS)
    a = ap.parse_args(argv)

    records = load_matrix(pathlib.Path(a.matrix))
    if a.pending:
        pending(records)
        return 0
    if not (a.record_id and a.by and (a.source or a.rejected)):
        ap.error("--record-id, --by and one of --source / --rejected are required")
    rec = next((r for r in records if r.get("record_id") == a.record_id), None)
    if rec is None:
        sys.exit("No record %s in %s. Run data/merge.py first." % (a.record_id, a.matrix))
    out = pathlib.Path(a.out)
    existing = [json.loads(l) for l in out.read_text().splitlines() if l.strip()] if out.exists() else []
    if any(e.get("record_id") == a.record_id for e in existing):
        sys.exit("An answer for %s already exists in %s. Remove it there first if it was wrong." % (a.record_id, out.name))
    entry = {"record_id": a.record_id, "confirmed_by": a.by, "date": datetime.date.today().isoformat()}
    if a.source:
        entry["model_confirmation"] = "human_confirmed"
        entry["model_confirmed_source"] = a.source.strip()
    else:
        entry["model_confirmation"] = "human_rejected"
    with out.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print("Recorded %s for %s (%s). Now run: python3 data/merge.py"
          % (entry["model_confirmation"], rec.get("device_local_id"), rec.get("tester")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
