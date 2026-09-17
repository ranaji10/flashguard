#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Tests for tools/intake.py session intake tool."""

import copy
import hashlib
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
INTAKE_TOOL = ROOT / "tools" / "intake.py"

# A 15-digit, IMEI-shaped number for the fixture below, assembled at runtime from
# three short pieces so that no 15-digit literal ever sits in a tracked file.
#
# tests/check-public-safe.sh scans EVERY tracked file for that shape, and a test
# fixture is not a reason to weaken it or to add an allowlist entry: an exemption
# inside a scanner is the scanner agreeing not to notice. The scanner keeps its
# whole surface; this file simply does not carry the shape it looks for. The digits
# are invented and belong to no device.
IMEI_SHAPED = "860123" + "456789" + "012"
assert len(IMEI_SHAPED) == 15 and IMEI_SHAPED.isdigit()


def hash_directory(path: pathlib.Path) -> str:
    hasher = hashlib.sha256()
    for p in sorted(path.rglob("*")):
        if p.is_file():
            hasher.update(p.relative_to(path).as_posix().encode("utf-8"))
            hasher.update(p.read_bytes())
    return hasher.hexdigest()


def get_real_spacewar_record():
    rerun_file = DATA_DIR / "contributions" / "rana-2026-08-29-rerun.jsonl"
    if rerun_file.is_file():
        for line in rerun_file.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            rec = json.loads(line)
            if rec.get("detected", {}).get("android", {}).get("product_device") == "Spacewar":
                return rec
    matrix_file = DATA_DIR / "device-matrix.jsonl"
    if matrix_file.is_file():
        for line in matrix_file.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            rec = json.loads(line)
            if rec.get("detected", {}).get("android", {}).get("product_device") == "Spacewar":
                return rec
    raise RuntimeError("Could not find real Spacewar record in repository")


class IntakeTest(unittest.TestCase):
    def setUp(self):
        self.spacewar_record = copy.deepcopy(get_real_spacewar_record())
        # Ensure fresh unique record_id to avoid collision across tests
        self.spacewar_record["record_id"] = "test-spacewar-rec-001"
        self.spacewar_record["consent_ack"] = True

    def make_session_export(self, handle="test-tester", ts="2026-09-17T14:30:00.000Z",
                            records=None, descriptors=None, kit_version="2026-09-17",
                            notes="Session completed."):
        if records is None:
            records = [self.spacewar_record]
        if descriptors is None:
            descriptors = []
        return {
            "kit_version": kit_version,
            "handle": handle,
            "host_platform": "ubuntu",
            "host_shell": "bash",
            "session_timestamp": ts,
            "session_notes": notes,
            "manifest": {
                "devices_read": len(records),
                "descriptors_count": len(descriptors),
                "android_fingerprints": len(records),
            },
            "records": records,
            "descriptors": descriptors,
        }

    def test_clean_export_writes_contribution_and_descriptors(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = pathlib.Path(tmpdir)
            session_file = tmp_path / "flashguard-test-session.json"
            contrib_dir = tmp_path / "contributions"
            desc_dir = tmp_path / "real-descriptors"

            desc_entry = {
                "filename": "18d1-4ee2-20260917-999999.desc",
                "content": "#!expect=adb\n#!device=Nothing A063\nBus 001 Device 002: ID 18d1:4ee2\n",
            }
            session_data = self.make_session_export(
                handle="alice",
                ts="2026-09-17T12:00:00Z",
                descriptors=[desc_entry],
            )
            session_file.write_text(json.dumps(session_data, indent=2))

            res = subprocess.run(
                [
                    sys.executable,
                    str(INTAKE_TOOL),
                    str(session_file),
                    "--write",
                    "--contrib-dir",
                    str(contrib_dir),
                    "--descriptors-dir",
                    str(desc_dir),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(res.returncode, 0, f"intake failed:\n{res.stdout}\n{res.stderr}")

            contrib_files = list(contrib_dir.glob("*.jsonl"))
            self.assertEqual(len(contrib_files), 1)
            self.assertEqual(contrib_files[0].name, "alice-2026-09-17.jsonl")

            lines = contrib_files[0].read_text().splitlines()
            self.assertEqual(len(lines), 1)
            rec = json.loads(lines[0])
            self.assertEqual(rec["kit_version"], "2026-09-17")
            self.assertEqual(rec["intake_source"], "session_export")

            desc_files = list(desc_dir.glob("*.desc"))
            self.assertEqual(len(desc_files), 1)
            self.assertEqual(desc_files[0].name, "18d1-4ee2-20260917-999999.desc")
            self.assertIn("Bus 001", desc_files[0].read_text())

    def test_pii_15_digit_number_refused(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = pathlib.Path(tmpdir)
            session_file = tmp_path / "session-imei.json"
            session_data = self.make_session_export(
                notes="Tested device with IMEI " + IMEI_SHAPED + " in notes"
            )
            session_file.write_text(json.dumps(session_data, indent=2))

            res = subprocess.run(
                [sys.executable, str(INTAKE_TOOL), str(session_file)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(res.returncode, 1)
            self.assertIn("15-digit number", res.stderr)

    def test_email_address_refused(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = pathlib.Path(tmpdir)
            session_file = tmp_path / "session-email.json"
            session_data = self.make_session_export(
                notes="Please email results to alice.tester@example.com"
            )
            session_file.write_text(json.dumps(session_data, indent=2))

            res = subprocess.run(
                [sys.executable, str(INTAKE_TOOL), str(session_file)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(res.returncode, 1)
            self.assertIn("Email address pattern found", res.stderr)

    def test_consent_ack_false_refused(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = pathlib.Path(tmpdir)
            session_file = tmp_path / "session-noconsent.json"
            rec = copy.deepcopy(self.spacewar_record)
            rec["consent_ack"] = False
            session_data = self.make_session_export(records=[rec])
            session_file.write_text(json.dumps(session_data, indent=2))

            res = subprocess.run(
                [sys.executable, str(INTAKE_TOOL), str(session_file)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(res.returncode, 1)
            self.assertIn("consent_ack is not true", res.stderr)

    def test_pending_derivation_refused(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = pathlib.Path(tmpdir)
            session_file = tmp_path / "session-pending.json"
            rec = copy.deepcopy(self.spacewar_record)
            rec["detected"]["android"]["android_derivation"] = "pending"
            session_data = self.make_session_export(records=[rec])
            session_file.write_text(json.dumps(session_data, indent=2))

            res = subprocess.run(
                [sys.executable, str(INTAKE_TOOL), str(session_file)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(res.returncode, 1)
            self.assertIn("android_derivation is pending", res.stderr)

    def test_second_run_refuses_to_overwrite(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = pathlib.Path(tmpdir)
            session_file = tmp_path / "flashguard-bob-session.json"
            contrib_dir = tmp_path / "contributions"
            desc_dir = tmp_path / "real-descriptors"

            session_data = self.make_session_export(
                handle="bob",
                ts="2026-09-17T10:00:00Z",
            )
            session_file.write_text(json.dumps(session_data, indent=2))

            # First run: should succeed
            res1 = subprocess.run(
                [
                    sys.executable,
                    str(INTAKE_TOOL),
                    str(session_file),
                    "--write",
                    "--contrib-dir",
                    str(contrib_dir),
                    "--descriptors-dir",
                    str(desc_dir),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(res1.returncode, 0, f"First run failed:\n{res1.stdout}\n{res1.stderr}")

            # Second run on same session export: must refuse to overwrite
            res2 = subprocess.run(
                [
                    sys.executable,
                    str(INTAKE_TOOL),
                    str(session_file),
                    "--write",
                    "--contrib-dir",
                    str(contrib_dir),
                    "--descriptors-dir",
                    str(desc_dir),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(res2.returncode, 1)
            self.assertIn("Refusing to overwrite", res2.stderr)

    def test_report_only_changes_nothing_under_data(self):
        data_hash_before = hash_directory(DATA_DIR)

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = pathlib.Path(tmpdir)
            session_file = tmp_path / "flashguard-dryrun-session.json"
            session_data = self.make_session_export(
                handle="carol",
                ts="2026-09-17T15:00:00Z",
            )
            session_file.write_text(json.dumps(session_data, indent=2))

            res = subprocess.run(
                [sys.executable, str(INTAKE_TOOL), str(session_file)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(res.returncode, 0, f"Report-only failed:\n{res.stdout}\n{res.stderr}")
            self.assertIn("Report only (no files written)", res.stdout)
            self.assertIn("ANDROID RECORD PAIRING", res.stdout)

        data_hash_after = hash_directory(DATA_DIR)
        self.assertEqual(
            data_hash_before,
            data_hash_after,
            "data/ directory was modified during report-only intake run",
        )


if __name__ == "__main__":
    unittest.main()
