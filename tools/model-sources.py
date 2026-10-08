#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Isolate every upstream source that relates to a device, and file them on a recipe.

Ruled 8 Oct 2026 (revised): the verifier settles a phone's model from credible public
sources, and asks the person only when they cannot. For that, a recipe carries:

  target.models_sources     the entries this recipe rests on, each with the model codes it
                            lists (an empty list means it names the device but no codes)
  target.competing_sources  entries sharing the codename that are NOT this recipe's device:
                            another LineageOS variant (6T vs 6T T-Mobile), or one listing
                            other model codes (Nord CE 3 Lite vs Nord N30). Shown to the
                            person if they are asked.

An entry is the recipe's own when it lists one of the recipe's model codes; failing that,
when it is a LineageOS variant with the recipe's install_method (if the method matches no
variant, none can be told apart and all are own); entries from projects without variants
(OpenAndroidInstaller, postmarketOS) are own when they list no codes.
Everything is read from the local clones under library/upstream; nothing is fetched.

Usage:
    python3 tools/model-sources.py fajita                     # print every related entry
    python3 tools/model-sources.py --recipe data/recipes-v0.2/spacewar.json --write
"""
import argparse
import collections
import datetime
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "data"))
import coverage  # noqa: E402

KEEP = ("project", "url", "name", "models", "install_method")


def split(entries, recipe):
    target = recipe.get("target", {})
    models = set(target.get("models") or [])
    method = recipe.get("install_method")
    own, competing = [], []
    # Variants are told apart by install method only when the recipe's method is one of
    # theirs; a recipe written from another project's vocabulary cannot tell them apart.
    split_by_method = any(e["project"] == "LineageOS" and not e["models"] and e.get("install_method") == method
                          for e in entries)
    for e in entries:
        if e["models"]:
            (own if models & set(e["models"]) else competing).append(e)
        elif e["project"] == "LineageOS" and split_by_method:
            (own if e.get("install_method") == method else competing).append(e)
        else:
            own.append(e)
    return own, competing


def entry_out(e, today):
    out = {k: e[k] for k in KEEP if k in e}
    out["consulted"] = today
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("codename", nargs="?")
    ap.add_argument("--recipe")
    ap.add_argument("--write", action="store_true", help="file the split into the recipe")
    ap.add_argument("--upstream", default=coverage.UPSTREAM, help=argparse.SUPPRESS)
    a = ap.parse_args(argv)
    today = datetime.date.today().isoformat()

    recipe = None
    if a.recipe:
        recipe = json.loads(pathlib.Path(a.recipe).read_text(encoding="utf-8"), object_pairs_hook=collections.OrderedDict)
    if recipe is None and not a.codename:
        ap.error("give a codename or --recipe")
    t = (recipe or {}).get("target", {})
    probe = {"codename": a.codename or t.get("product_device")}
    entries = coverage.upstream_entries(probe, a.upstream)
    aliases = set(t.get("supported_device_codes") or [])
    for alias in aliases:
        for e in coverage.upstream_entries({"codename": alias}, a.upstream):
            if e not in entries:
                entries.append(e)
    if not entries:
        print("No upstream entry relates to %s." % probe["codename"])
        return 1

    if recipe is None:
        for e in entries:
            print("%-22s %-40s %-28s %s" % (e["project"], e["name"][:40], ",".join(e["models"]) or "(no model codes)", e["url"]))
        return 0

    own, competing = split(entries, recipe)
    for label, group in (("this recipe", own), ("cannot tell apart from", competing)):
        print("  %s:" % label)
        for e in group:
            print("    %-22s %-34s %-24s %s" % (e["project"], e["name"][:34], ",".join(e["models"]) or "(no codes)", e["url"]))
    if a.write:
        new = collections.OrderedDict()
        for k, v in recipe["target"].items():
            if k in ("models_sources", "competing_sources"):
                continue
            new[k] = v
            if k == "models":
                new["models_sources"] = [entry_out(e, today) for e in own]
                new["competing_sources"] = [entry_out(e, today) for e in competing]
        if "models_sources" not in new:
            new["models_sources"] = [entry_out(e, today) for e in own]
            new["competing_sources"] = [entry_out(e, today) for e in competing]
        recipe["target"] = new
        path = pathlib.Path(a.recipe)
        raw = path.read_text(encoding="utf-8")
        if "\n  " in raw:
            text = json.dumps(recipe, indent=2, ensure_ascii=False) + "\n"
        else:
            text = json.dumps(recipe, separators=(",", ":"), ensure_ascii=False) + "\n"
        path.write_text(text, encoding="utf-8")
        print("  wrote %s" % path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
