#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""
Build the canonical device matrix from tester contributions.

    python3 merge.py                 # rebuild device-matrix.jsonl, print a report
    python3 merge.py --check         # validate only, write nothing (use in CI)

Contributions are dropped in contributions/ as returned, one file per tester per
session, and are never edited by hand. device-matrix.jsonl is GENERATED. If you
find yourself editing it, you are about to lose provenance.

    contributions/rana-2026-08-29.jsonl   ->
    contributions/priya-2026-09-14.jsonl  ->  device-matrix.jsonl
    contributions/j-doe-2026-09-15.jsonl  ->

A file renamed to *.superseded.jsonl is kept on disk and reported, but is not
merged. That is how a run captured by a version of the tooling now known to be
wrong is retired without destroying the evidence that it happened.

Why a merge step rather than one shared file: fifteen testers appending to one
file is a merge conflict every time, and there is no way to withdraw one person's
data afterwards. One file per submission means a withdrawal is `rm one file` plus
a rebuild, which is what participation-note.md promises.
"""
import json, sys, re, hashlib, collections, pathlib

HERE = pathlib.Path(__file__).parent
CONTRIB = HERE / "contributions"
OUT = HERE / "device-matrix.jsonl"

FORBIDDEN = re.compile(
    r"\b(imei|imsi|iccid|serialno|serial_no|iSerial|android_id)\b", re.I)
# 15-digit IMEI, or a MAC address. Cheap tripwires, not a guarantee.
LOOKS_LIKE_IMEI = re.compile(r"(?<!\d)\d{15}(?!\d)")
LOOKS_LIKE_MAC = re.compile(r"\b([0-9a-f]{2}:){5}[0-9a-f]{2}\b", re.I)

def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-") or "unnamed"

def device_key(rec):
    """Stable identity for one physical device.

    Preference order:
      1. device_local_id the tester assigned  -- the only unit-level truth we have
      2. tester + reported_device            -- works when they named it consistently
      3. tester + vendor:product             -- model-level, collides between two
                                                identical phones owned by one person
    Never a serial number. The matrix is published.
    """
    t = slug(rec.get("tester"))
    if rec.get("device_local_id"):
        return f"{t}/{slug(rec['device_local_id'])}", "local_id"
    if rec.get("reported_device") and rec.get("identity_source") == "tester_identified":
        return f"{t}/{slug(rec['reported_device'])}", "reported_device"
    d = rec.get("detected", {})
    return f"{t}/{d.get('usb_vendor_id','?')}-{d.get('usb_product_id','?')}", "vendor_product"

def scan_pii(raw, where, problems):
    for pat, what in ((FORBIDDEN, "forbidden field name"),
                      (LOOKS_LIKE_IMEI, "15-digit number (IMEI?)"),
                      (LOOKS_LIKE_MAC, "MAC address")):
        m = pat.search(raw)
        if m:
            problems.append(f"{where}: {what}: {m.group(0)[:24]}")

def main():
    check_only = "--check" in sys.argv
    problems, records, seen_ids = [], [], {}

    files = [f for f in sorted(CONTRIB.glob("*.jsonl"))
             if not f.name.endswith(".superseded.jsonl")]
    retired = sorted(CONTRIB.glob("*.superseded.jsonl"))
    if not files:
        print(f"No contributions in {CONTRIB}/. Nothing to merge.")
        return 0

    for f in files:
        for n, line in enumerate(f.read_text().splitlines(), 1):
            line = line.strip()
            if not line:
                continue
            where = f"{f.name}:{n}"
            scan_pii(line, where, problems)
            try:
                rec = json.loads(line)
            except json.JSONDecodeError as e:
                problems.append(f"{where}: not valid JSON: {e}")
                continue
            rid = rec.get("record_id")
            if not rid:
                problems.append(f"{where}: no record_id")
            elif rid in seen_ids:
                problems.append(f"{where}: duplicate record_id, first seen {seen_ids[rid]}")
                continue
            else:
                seen_ids[rid] = where
            if not rec.get("consent_ack"):
                problems.append(f"{where}: consent_ack missing or false -- NOT PUBLISHED")
                continue
            rec["_source_file"] = f.name
            k, how = device_key(rec)
            rec["device_key"] = k
            rec["device_key_basis"] = how
            records.append(rec)

    # group observations by physical device
    devices = collections.OrderedDict()
    for r in records:
        devices.setdefault(r["device_key"], []).append(r)
    for k, obs in devices.items():
        obs.sort(key=lambda r: (r.get("date", ""), r.get("record_id", "")))
        for i, r in enumerate(obs, 1):
            r["capture_seq"] = i
            r["capture_count"] = len(obs)
            r["related_records"] = [o["record_id"] for o in obs
                                    if o.get("record_id") != r.get("record_id")]

    print(f"\n  {len(files)} contribution file(s)")
    if retired:
        print(f"  {len(retired)} superseded file(s) kept but not merged: "
              + ", ".join(f.name for f in retired))
    print(f"  {len(records)} usable records")
    print(f"  {len(devices)} distinct physical devices\n")

    multi = {k: v for k, v in devices.items() if len(v) > 1}
    if multi:
        print("  Devices captured more than once:")
        for k, v in multi.items():
            classes = collections.Counter(
                r.get("detected", {}).get("device_class", "?") for r in v)
            modes = [r.get("device_mode", "default") for r in v]
            flag = "  <-- DISAGREES ACROSS CAPTURES" if len(classes) > 1 else ""
            print(f"    {k:<40} {len(v):>2} captures  "
                  f"{dict(classes)}  modes={sorted(set(modes))}{flag}")
        print()

    basis = collections.Counter(r["device_key_basis"] for r in records)
    if basis.get("vendor_product"):
        print(f"  {basis['vendor_product']} record(s) keyed on vendor:product alone.")
        print("  Two identical devices owned by one tester would merge into one.")
        print("  Ask those testers to label their devices.\n")

    if problems:
        print("  PROBLEMS")
        for p in problems:
            print(f"    {p}")
        print()

    if check_only:
        return 1 if problems else 0

    with OUT.open("w") as fh:
        for r in records:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"  wrote {OUT.name}\n")
    return 1 if problems else 0

if __name__ == "__main__":
    sys.exit(main())
