#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Session export intake tool for Flashguard.

Imports a returned session export JSON from a tester into the repository:
validates integrity, scans for PII/serials/emails, ensures consent and derivation,
writes contributions and descriptors, checks merge validity, and reports pairing
verdicts for the organiser.

Usage:
    python3 tools/intake.py <path/to/flashguard-handle-timestamp.json>          # report only
    python3 tools/intake.py <path/to/flashguard-handle-timestamp.json> --write  # write contribution
"""

import argparse
import copy
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
CONTRIB_DIR = DATA_DIR / "contributions"
REAL_DESCRIPTORS = ROOT / "tests" / "real-descriptors"
RECIPE_DIRS = (DATA_DIR / "recipes", DATA_DIR / "recipes-v0.2")

# Ensure modules in data and flashguard can be imported
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(DATA_DIR) not in sys.path:
    sys.path.insert(0, str(DATA_DIR))

try:
    import merge
    from merge import scan_pii, slug
except ImportError as err:
    sys.exit(f"Failed to import merge module: {err}")

try:
    from flashguard.verify import verify
except ImportError as err:
    sys.exit(f"Failed to import flashguard.verify: {err}")

EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Flashguard session export intake tool."
    )
    parser.add_argument("session_file", help="Path to session export JSON file")
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write contribution file and descriptors to repository",
    )
    parser.add_argument(
        "--legacy-kit",
        action="store_true",
        help="Allow session export without kit_version",
    )
    parser.add_argument(
        "--session-number",
        type=int,
        default=1,
        help="Session sequence number on same day (e.g. 2 for <handle>-<date>-2.jsonl)",
    )
    parser.add_argument(
        "--contrib-dir",
        type=pathlib.Path,
        default=None,
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--descriptors-dir",
        type=pathlib.Path,
        default=None,
        help=argparse.SUPPRESS,
    )
    return parser.parse_args()


def load_recipes(recipe_dirs=RECIPE_DIRS):
    recipes = []
    for rdir in recipe_dirs:
        if not rdir.is_dir():
            continue
        for f in sorted(rdir.glob("*.json")):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                recipes.append((f.name, data))
            except Exception:
                pass
    return recipes


def report_android_pairing(records, recipes):
    print("\n--- ANDROID RECORD PAIRING & VERIFICATION REPORT ---")
    android_count = 0
    for i, rec in enumerate(records, 1):
        detected = rec.get("detected") or {}
        android = detected.get("android") or {}
        dev_class = detected.get("device_class")
        product_device = android.get("product_device")
        product_model = android.get("product_model")

        is_android = dev_class in ("adb", "fastboot") or (
            product_device and product_device != "not_applicable"
        )
        if not is_android:
            continue

        android_count += 1
        rec_id = rec.get("record_id") or rec.get("device_local_id") or f"record_{i}"
        print(f"\nRecord: {rec_id}")
        print(f"  product_device: {product_device}")
        print(f"  product_model:  {product_model}")

        # Match recipes
        dev_lower = (product_device or "").lower()
        paired = []
        for rname, recipe in recipes:
            target = recipe.get("target") or {}
            target_device = (target.get("product_device") or "").lower()
            target_aliases = [
                code.lower() for code in target.get("supported_device_codes", [])
            ]
            if dev_lower and dev_lower != "not_applicable" and (
                dev_lower == target_device or dev_lower in target_aliases
            ):
                paired.append((rname, recipe))

        if not paired:
            print("  Paired recipes: none matching this product_device")
            continue

        print(f"  Paired recipes: {len(paired)}")
        for rname, recipe in paired:
            recipe_id = recipe.get("recipe_id", rname)
            res = verify(dict(android), recipe)
            verdict = res.get("verdict")
            non_pass_reasons = [
                r.get("code") for r in res.get("reasons", []) if r.get("result") != "pass"
            ]
            print(f"    - {recipe_id}")
            print(f"        verdict: {verdict}")
            if non_pass_reasons:
                print(f"        non-pass reason codes: {', '.join(non_pass_reasons)}")
            else:
                print("        non-pass reason codes: (none)")

    if android_count == 0:
        print("No Android records found in session export.")
    print("----------------------------------------------------\n")


def run_intake(session_path, write=False, legacy_kit=False, session_number=1,
               target_contrib_dir=None, target_descriptors_dir=None):
    if not session_path.is_file():
        sys.exit(f"Session export file not found: {session_path}")

    file_text = session_path.read_text(encoding="utf-8")

    # Step 1: Parse session export and require top-level fields
    try:
        data = json.loads(file_text)
    except json.JSONDecodeError as err:
        sys.exit(f"Session export is not valid JSON: {err}")

    if not isinstance(data, dict):
        sys.exit("Session export root must be a JSON object")

    handle = data.get("handle")
    if not handle or not isinstance(handle, str) or not handle.strip():
        sys.exit("Missing or empty 'handle' in session export")

    session_timestamp = data.get("session_timestamp")
    if not session_timestamp or not isinstance(session_timestamp, str) or not session_timestamp.strip():
        sys.exit("Missing or empty 'session_timestamp' in session export")

    records = data.get("records")
    if not isinstance(records, list) or len(records) == 0:
        sys.exit("Missing or empty 'records' in session export")

    kit_version = data.get("kit_version")
    if not kit_version:
        if legacy_kit:
            print("Notice: 'kit_version' missing in session export (permitted by --legacy-kit)")
            kit_version = "legacy"
        else:
            sys.exit("Missing 'kit_version' in session export (use --legacy-kit to allow)")

    # Step 2: Run scan_pii from data/merge.py over whole file text
    problems = []
    scan_pii(file_text, session_path.name, problems)
    if problems:
        print("PII scan failed: forbidden field, serial, or identifier detected:", file=sys.stderr)
        for p in problems:
            print(f"  {p[:120]}", file=sys.stderr)
        sys.exit(1)

    # Step 3: Refuse any record with consent_ack not true or android_derivation pending
    for i, rec in enumerate(records, 1):
        rec_name = rec.get("record_id") or rec.get("device_local_id") or f"record_{i}"
        if rec.get("consent_ack") is not True:
            sys.exit(f"Record {rec_name}: consent_ack is not true ({rec.get('consent_ack')!r})")
        android_block = rec.get("detected", {}).get("android", {})
        if isinstance(android_block, dict) and android_block.get("android_derivation") == "pending":
            sys.exit(f"Record {rec_name}: android_derivation is pending -- derivation has not been run")

    # Step 4: No email address in any output/session file
    email_match = EMAIL_PATTERN.search(file_text)
    if email_match:
        sys.exit(f"Email address pattern found in session export: {email_match.group(0)[:50]}")

    # Determine contribution filename
    date_match = re.search(r"(\d{4}-\d{2}-\d{2})", session_timestamp)
    if not date_match:
        sys.exit(f"Cannot extract YYYY-MM-DD from session_timestamp: {session_timestamp}")
    date_str = date_match.group(1)
    handle_slug = slug(handle)

    if session_number > 1:
        contrib_filename = f"{handle_slug}-{date_str}-{session_number}.jsonl"
    else:
        contrib_filename = f"{handle_slug}-{date_str}.jsonl"

    dest_contrib_dir = target_contrib_dir or CONTRIB_DIR
    dest_descriptors_dir = target_descriptors_dir or REAL_DESCRIPTORS

    contrib_dest_path = dest_contrib_dir / contrib_filename

    # Step 5: Check if contribution file already exists
    if contrib_dest_path.exists():
        sys.exit(
            f"Contribution file already exists: {contrib_dest_path}. Refusing to overwrite. "
            f"(A second session the same day is {handle_slug}-{date_str}-2.jsonl)"
        )

    # Step 6: Check descriptors overwrite
    descriptors = data.get("descriptors") or []
    for desc in descriptors:
        fname = desc.get("filename")
        if fname:
            target_desc_path = dest_descriptors_dir / fname
            if target_desc_path.exists():
                sys.exit(f"Descriptor file already exists: {target_desc_path}. Refusing to overwrite.")

    # Prepare enriched records
    prepared_records = copy.deepcopy(records)
    for rec in prepared_records:
        rec["kit_version"] = kit_version
        rec["intake_source"] = "session_export"

    recipes = load_recipes()

    if write:
        # Step 5, 6, 7 writing to target repository directories
        created_files = []
        try:
            dest_contrib_dir.mkdir(parents=True, exist_ok=True)
            with open(contrib_dest_path, "w", encoding="utf-8") as fh:
                for rec in prepared_records:
                    fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            created_files.append(contrib_dest_path)

            dest_descriptors_dir.mkdir(parents=True, exist_ok=True)
            for desc in descriptors:
                fname = desc.get("filename")
                content = desc.get("content")
                if fname and content:
                    dpath = dest_descriptors_dir / fname
                    dpath.write_text(content, encoding="utf-8")
                    created_files.append(dpath)

            # Check descriptor privacy if writing to repo real-descriptors
            if dest_descriptors_dir == REAL_DESCRIPTORS:
                res = subprocess.run(
                    ["bash", str(ROOT / "tests" / "check-descriptor-privacy.sh")],
                    capture_output=True,
                    text=True,
                )
                if res.returncode != 0:
                    print(res.stdout, file=sys.stderr)
                    print(res.stderr, file=sys.stderr)
                    raise RuntimeError("check-descriptor-privacy failed")

            # Check merge.py --check
            if dest_contrib_dir == CONTRIB_DIR:
                res = subprocess.run(
                    [sys.executable, str(DATA_DIR / "merge.py"), "--check"],
                    capture_output=True,
                    text=True,
                )
                if res.returncode != 0:
                    print(res.stdout, file=sys.stderr)
                    print(res.stderr, file=sys.stderr)
                    raise RuntimeError("data/merge.py --check failed")
            else:
                # Custom contrib dir validation
                code = f"""
import sys, pathlib, merge
merge.CONTRIB = pathlib.Path({repr(str(dest_contrib_dir))})
merge.OUT = pathlib.Path({repr(str(dest_contrib_dir.parent / 'device-matrix.jsonl'))})
sys.argv = ['merge.py', '--check']
sys.exit(merge.main())
"""
                res = subprocess.run(
                    [sys.executable, "-c", code],
                    cwd=str(DATA_DIR),
                    capture_output=True,
                    text=True,
                )
                if res.returncode != 0:
                    print(res.stdout, file=sys.stderr)
                    print(res.stderr, file=sys.stderr)
                    raise RuntimeError("custom merge validation failed")

        except Exception as exc:
            for f in created_files:
                if f.exists():
                    try:
                        f.unlink()
                    except Exception:
                        pass
            sys.exit(f"Error during intake write: {exc}")

        print(f"Successfully wrote contribution to {contrib_dest_path}")
        if len(created_files) > 1:
            print(f"Wrote {len(created_files) - 1} descriptor file(s) to {dest_descriptors_dir}")

        # Step 8: Pairing report
        report_android_pairing(prepared_records, recipes)

        print("Next steps for the organiser:")
        print("  python3 data/merge.py")
        print("  python3 data/coverage.py")
        print(f"  git add data/contributions/{contrib_filename}")
        for desc in descriptors:
            fname = desc.get("filename")
            if fname:
                print(f"  git add tests/real-descriptors/{fname}")
        print("  git commit\n")

    else:
        # Report only: test steps 5 to 7 against a temp copy of data/
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_root = pathlib.Path(tmpdir)
            tmp_contrib = tmp_root / "contributions"
            tmp_descriptors = tmp_root / "real-descriptors"

            if CONTRIB_DIR.is_dir():
                shutil.copytree(CONTRIB_DIR, tmp_contrib)
            else:
                tmp_contrib.mkdir()
            tmp_descriptors.mkdir()

            tmp_contrib_file = tmp_contrib / contrib_filename
            with open(tmp_contrib_file, "w", encoding="utf-8") as fh:
                for rec in prepared_records:
                    fh.write(json.dumps(rec, ensure_ascii=False) + "\n")

            for desc in descriptors:
                fname = desc.get("filename")
                content = desc.get("content")
                if fname and content:
                    (tmp_descriptors / fname).write_text(content, encoding="utf-8")

            # Validate merge on temp directory
            code = f"""
import sys, pathlib, merge
merge.CONTRIB = pathlib.Path({repr(str(tmp_contrib))})
merge.OUT = pathlib.Path({repr(str(tmp_root / 'device-matrix.jsonl'))})
sys.argv = ['merge.py', '--check']
sys.exit(merge.main())
"""
            res = subprocess.run(
                [sys.executable, "-c", code],
                cwd=str(DATA_DIR),
                capture_output=True,
                text=True,
            )
            if res.returncode != 0:
                print(res.stdout, file=sys.stderr)
                print(res.stderr, file=sys.stderr)
                sys.exit(f"data/merge.py --check failed in dry run validation")

        print("Report only (no files written). Session export validated successfully.")
        print(f"Target contribution would be: data/contributions/{contrib_filename}")
        if descriptors:
            print(f"Target descriptors count: {len(descriptors)}")

        # Step 8: Pairing report
        report_android_pairing(prepared_records, recipes)


def main():
    args = parse_args()
    session_path = pathlib.Path(args.session_file).resolve()
    run_intake(
        session_path=session_path,
        write=args.write,
        legacy_kit=args.legacy_kit,
        session_number=args.session_number,
        target_contrib_dir=args.contrib_dir,
        target_descriptors_dir=args.descriptors_dir,
    )


if __name__ == "__main__":
    main()
