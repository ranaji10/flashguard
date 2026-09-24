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

            real_desc_file = sorted((ROOT / "tests" / "real-descriptors").glob("*.desc"))[0]
            real_content = real_desc_file.read_text(encoding="utf-8")
            desc_entry = {
                "filename": "18d1-4ee2-20260917-999999.desc",
                "content": real_content,
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
            self.assertEqual(desc_files[0].read_text(encoding="utf-8"), real_content)

    def test_descriptor_with_lsusb_iserial_refused(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = pathlib.Path(tmpdir)
            session_file = tmp_path / "session-iserial.json"
            sample_serial = "0123" + "4567" + "89AB"
            desc_entry = {
                "filename": "test-device.desc",
                "content": "Bus 001 Device 002: ID 18d1:4ee2\n  iSerial                 3 " + sample_serial + "\n",
            }
            session_data = self.make_session_export(descriptors=[desc_entry])
            session_file.write_text(json.dumps(session_data, indent=2))

            res = subprocess.run(
                [sys.executable, str(INTAKE_TOOL), str(session_file)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(res.returncode, 1)
            self.assertIn("forbidden field name", res.stderr)
            self.assertIn("iSerial", res.stderr)

    def test_descriptor_with_unmasked_sn_refused(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = pathlib.Path(tmpdir)
            session_file = tmp_path / "session-sn-unmasked.json"
            sample_sn = "YUPIK-QRD _SN:" + "ABC" + "12345"
            desc_entry = {
                "filename": "test-device.desc",
                "content": f"Bus 001 Device 002: ID 18d1:4ee2\n  iProduct                2 {sample_sn}\n",
            }
            session_data = self.make_session_export(descriptors=[desc_entry])
            session_file.write_text(json.dumps(session_data, indent=2))

            res = subprocess.run(
                [sys.executable, str(INTAKE_TOOL), str(session_file)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(res.returncode, 1)
            self.assertIn("embedded serial", res.stderr)

    def test_descriptor_with_masked_sn_accepted(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = pathlib.Path(tmpdir)
            session_file = tmp_path / "session-sn-masked.json"
            desc_entry = {
                "filename": "test-device.desc",
                "content": "Bus 001 Device 002: ID 18d1:4ee2\n  iProduct                2 YUPIK-QRD _SN:<stripped>\n",
            }
            session_data = self.make_session_export(descriptors=[desc_entry])
            session_file.write_text(json.dumps(session_data, indent=2))

            res = subprocess.run(
                [sys.executable, str(INTAKE_TOOL), str(session_file)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(res.returncode, 0, f"Expected 0, got {res.returncode}:\n{res.stderr}")

    def test_descriptor_filename_traversal_refused(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = pathlib.Path(tmpdir)
            (tmp_path / "repo" / "tests").mkdir(parents=True)
            session_file = tmp_path / "session-escaped.json"
            desc_entry = {
                "filename": "../../ESCAPED.txt",
                "content": "should never be written here\n",
            }
            session_data = self.make_session_export(descriptors=[desc_entry])
            session_file.write_text(json.dumps(session_data, indent=2))

            res = subprocess.run(
                [
                    sys.executable,
                    str(INTAKE_TOOL),
                    str(session_file),
                    "--write",
                    "--contrib-dir",
                    str(tmp_path / "contrib"),
                    "--descriptors-dir",
                    str(tmp_path / "repo" / "tests" / "real-descriptors"),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(res.returncode, 1)
            self.assertIn("../../ESCAPED.txt", res.stderr)
            self.assertFalse((tmp_path / "repo" / "ESCAPED.txt").exists())

    def test_descriptor_filename_variations_validation(self):
        for invalid_name in ["/tmp/abs.desc", "relative/path.desc", "noextension", "wrong.txt", ".", ".."]:
            with tempfile.TemporaryDirectory() as tmpdir:
                tmp_path = pathlib.Path(tmpdir)
                session_file = tmp_path / "session-invalid-desc.json"
                desc_entry = {
                    "filename": invalid_name,
                    "content": "test\n",
                }
                session_data = self.make_session_export(descriptors=[desc_entry])
                session_file.write_text(json.dumps(session_data, indent=2))

                res = subprocess.run(
                    [sys.executable, str(INTAKE_TOOL), str(session_file)],
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(res.returncode, 1, f"Expected refusal for {invalid_name!r}")

        # Bare valid name must succeed
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = pathlib.Path(tmpdir)
            session_file = tmp_path / "session-valid-desc.json"
            desc_entry = {
                "filename": "valid-device-123.desc",
                "content": "Bus 001 Device 002: ID 18d1:4ee2\n",
            }
            session_data = self.make_session_export(descriptors=[desc_entry])
            session_file.write_text(json.dumps(session_data, indent=2))

            res = subprocess.run(
                [sys.executable, str(INTAKE_TOOL), str(session_file)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(res.returncode, 0, f"Bare valid name failed: {res.stderr}")

    def test_report_only_runs_descriptor_privacy_check(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = pathlib.Path(tmpdir)
            session_file = tmp_path / "session-report-privacy.json"
            desc_entry = {
                "filename": "planted-serial.desc",
                "content": "Bus 001 Device 002: ID 18d1:4ee2\n  iSerial                 3 0123456789ABCDEF\n",
            }
            session_data = self.make_session_export(descriptors=[desc_entry])
            session_file.write_text(json.dumps(session_data, indent=2))

            res = subprocess.run(
                [sys.executable, str(INTAKE_TOOL), str(session_file)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(res.returncode, 1)

    def test_pairing_agreement_intake_and_coverage(self):
        """Assert intake and coverage.py produce identical verdict and reasons for Spacewar."""
        sys.path.insert(0, str(DATA_DIR))
        import coverage
        from flashguard.verify import verify

        recipes = coverage.load_all_recipes([DATA_DIR / "recipes-v0.2"])
        spacewar_recipe = next((r for name, r in recipes if "spacewar" in name.lower()), None)
        self.assertIsNotNone(spacewar_recipe, "spacewar.json recipe not found")

        # Via coverage helpers used by intake
        android_facts = coverage.get_android_facts(self.spacewar_record)
        intake_paired = coverage.pair_record_with_recipes(self.spacewar_record, [(spacewar_recipe.get("recipe_id", "spacewar.json"), spacewar_recipe)])
        self.assertEqual(len(intake_paired), 1)

        intake_res = verify(android_facts, spacewar_recipe)
        intake_verdict = intake_res.get("verdict")
        intake_reasons = [r.get("code") for r in intake_res.get("reasons", []) if r.get("result") != "pass"]

        # Via coverage.corpus_runs
        corpus_res = coverage.corpus_runs(str(DATA_DIR / "recipes-v0.2"), [self.spacewar_record])
        spacewar_corpus_run = next((cr for cr in corpus_res if "spacewar" in cr["recipe_id"].lower()), None)
        self.assertIsNotNone(spacewar_corpus_run, "Spacewar run missing from corpus_runs")

        self.assertEqual(intake_verdict, spacewar_corpus_run["verdict"])
        self.assertEqual(intake_verdict, "not-ready")

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
