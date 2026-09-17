#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Derive pending Android properties in a Flashguard session export.

Reads a session export JSON file containing raw Android property captures
(captured e.g. on Windows via PowerShell/cmd without bash, where android_derivation
is 'pending'). For each record with android_derivation: 'pending', pipes the raw
property text through bench-kit/scripts/derive.sh, populates the derived fields,
and sets android_derivation: 'derived'.

Writes a new file next to the input named <name>-derived.json. Refuses to overwrite.

REQUIREMENT: Requires bash. This tool runs on macOS or Linux (e.g. the maintainer's
MacBook) to process session files brought from Windows capture machines. It will
not run on Windows directly.
"""

import argparse
import copy
import json
import os
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DERIVE_SCRIPT = ROOT / "bench-kit" / "scripts" / "derive.sh"


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Derive pending Android properties in a Flashguard session export. "
            "Requires bash (runs on macOS/Linux, not on Windows)."
        )
    )
    parser.add_argument("session_file", help="Path to session export JSON file")
    return parser.parse_args()


def derive_android_raw(raw_text: str, script_path: pathlib.Path) -> dict:
    proc = subprocess.run(
        ["bash", str(script_path)],
        input=raw_text,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"derive.sh failed with exit code {proc.returncode}:\n{proc.stderr}")

    derived = {}
    for line in proc.stdout.splitlines():
        if not line.strip() or "\t" not in line:
            continue
        k, v = line.split("\t", 1)
        derived[k] = v
    return derived


def derive_pending_session(session_path: pathlib.Path) -> pathlib.Path:
    if not session_path.is_file():
        sys.exit(f"Session file not found: {session_path}")

    if not DERIVE_SCRIPT.is_file():
        sys.exit(f"derive.sh not found at expected path: {DERIVE_SCRIPT}")

    # Output file: <name>-derived.json next to input
    stem = session_path.stem
    out_name = f"{stem}-derived.json"
    out_path = session_path.parent / out_name

    if out_path.exists():
        sys.exit(f"Derived output file already exists: {out_path}. Refusing to overwrite.")

    try:
        data = json.loads(session_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as err:
        sys.exit(f"Session export is not valid JSON: {err}")

    if not isinstance(data, dict):
        sys.exit("Session export root must be a JSON object")

    records = data.get("records")
    if not isinstance(records, list):
        sys.exit("Session export missing 'records' list")

    derived_count = 0
    updated_records = []
    for rec in records:
        rec_copy = copy.deepcopy(rec)
        detected = rec_copy.get("detected")
        if isinstance(detected, dict):
            android_block = detected.get("android")
            if (
                isinstance(android_block, dict)
                and "android_raw" in android_block
                and android_block.get("android_derivation") == "pending"
            ):
                raw_text = android_block.get("android_raw") or ""
                derived_fields = derive_android_raw(raw_text, DERIVE_SCRIPT)
                android_block["android_derivation"] = "derived"
                android_block.update(derived_fields)
                derived_count += 1
        updated_records.append(rec_copy)

    out_data = copy.deepcopy(data)
    out_data["records"] = updated_records

    out_path.write_text(json.dumps(out_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Derived {derived_count} pending record(s). Wrote output to: {out_path}")
    return out_path


def main():
    args = parse_args()
    session_path = pathlib.Path(args.session_file).resolve()
    derive_pending_session(session_path)


if __name__ == "__main__":
    main()
