#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Tests for tools/derive-pending.py derivation tool."""

import copy
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
DERIVE_PENDING_TOOL = ROOT / "tools" / "derive-pending.py"
INTAKE_TOOL = ROOT / "tools" / "intake.py"
DERIVE_SCRIPT = ROOT / "bench-kit" / "scripts" / "derive.sh"
ANDROID_FIXTURES = ROOT / "tests" / "android"


def run_derive_script(raw_text: str) -> dict:
    proc = subprocess.run(
        ["bash", str(DERIVE_SCRIPT)],
        input=raw_text,
        capture_output=True,
        text=True,
        check=True,
    )
    res = {}
    for line in proc.stdout.splitlines():
        if "\t" in line:
            k, v = line.split("\t", 1)
            res[k] = v
    return res


class DerivePendingTest(unittest.TestCase):
    def make_session(self, records, handle="test-tester", ts="2026-09-17T14:30:00Z"):
        return {
            "kit_version": "2026-09-17",
            "handle": handle,
            "host_platform": "windows",
            "host_shell": "powershell",
            "session_timestamp": ts,
            "session_notes": "Windows capture session",
            "manifest": {
                "devices_read": len(records),
                "descriptors_count": 0,
                "android_fingerprints": len(records),
            },
            "records": records,
            "descriptors": [],
        }

    def test_samsung_a5_derivation(self):
        props_file = ANDROID_FIXTURES / "samsung-a5-2017-android8.props"
        self.assertTrue(props_file.is_file(), f"Missing fixture: {props_file}")
        raw_text = "\n".join(
            line for line in props_file.read_text(encoding="utf-8").splitlines()
            if not line.startswith("#!")
        )

        expected_from_script = run_derive_script(raw_text)

        rec = {
            "schema_version": "0.4",
            "record_id": "test-samsung-pending-01",
            "tester": "test-tester",
            "consent_ack": True,
            "date": "2026-09-17",
            "host_platform": "windows",
            "capture_route": "adb_host",
            "reported_device": "Samsung Galaxy A5 (2017)",
            "device_local_id": "samsung-a5",
            "detected": {
                "usb_vendor_id": "0x04e8",
                "usb_product_id": "0x6860",
                "device_class": "adb",
                "android": {
                    "android_raw": raw_text,
                    "android_derivation": "pending",
                },
            },
            "identity_source": "tester_identified",
            "classification_correct": True,
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = pathlib.Path(tmpdir)
            session_file = tmp_path / "flashguard-session.json"
            session_file.write_text(json.dumps(self.make_session([rec]), indent=2))

            res = subprocess.run(
                [sys.executable, str(DERIVE_PENDING_TOOL), str(session_file)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(res.returncode, 0, f"derive-pending failed:\n{res.stderr}")

            derived_file = tmp_path / "flashguard-session-derived.json"
            self.assertTrue(derived_file.is_file(), "Derived output file was not created")

            derived_data = json.loads(derived_file.read_text(encoding="utf-8"))
            derived_rec = derived_data["records"][0]
            android = derived_rec["detected"]["android"]

            self.assertEqual(android["android_derivation"], "derived")
            self.assertEqual(android["android_raw"], raw_text)
            self.assertEqual(android["partition_scheme"], expected_from_script.get("partition_scheme"))
            self.assertEqual(android["bootloader_state"], expected_from_script.get("bootloader_state"))
            self.assertEqual(android["chipset_family"], expected_from_script.get("chipset_family"))

    def test_empty_props_derivation(self):
        props_file = ANDROID_FIXTURES / "empty-everything.props"
        self.assertTrue(props_file.is_file(), f"Missing fixture: {props_file}")
        raw_text = "\n".join(
            line for line in props_file.read_text(encoding="utf-8").splitlines()
            if not line.startswith("#!")
        )

        rec = {
            "schema_version": "0.4",
            "record_id": "test-empty-pending-02",
            "tester": "test-tester",
            "consent_ack": True,
            "date": "2026-09-17",
            "host_platform": "windows",
            "capture_route": "adb_host",
            "reported_device": "Unknown Device",
            "device_local_id": "unknown-dev",
            "detected": {
                "usb_vendor_id": "0x0000",
                "usb_product_id": "0x0000",
                "device_class": "adb",
                "android": {
                    "android_raw": raw_text,
                    "android_derivation": "pending",
                },
            },
            "identity_source": "tester_identified",
            "classification_correct": True,
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = pathlib.Path(tmpdir)
            session_file = tmp_path / "flashguard-empty-session.json"
            session_file.write_text(json.dumps(self.make_session([rec]), indent=2))

            res = subprocess.run(
                [sys.executable, str(DERIVE_PENDING_TOOL), str(session_file)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(res.returncode, 0, f"derive-pending failed on empty props:\n{res.stderr}")

            derived_file = tmp_path / "flashguard-empty-session-derived.json"
            derived_data = json.loads(derived_file.read_text(encoding="utf-8"))
            android = derived_data["records"][0]["detected"]["android"]

            self.assertEqual(android["android_derivation"], "derived")
            self.assertEqual(android["partition_scheme"], "unknown")
            self.assertEqual(android["bootloader_state"], "unknown")
            self.assertEqual(android["chipset_family"], "unknown")

    def test_record_with_no_android_raw_unchanged(self):
        non_android_rec = {
            "schema_version": "0.4",
            "record_id": "test-usb-stick-03",
            "tester": "test-tester",
            "consent_ack": True,
            "date": "2026-09-17",
            "host_platform": "windows",
            "capture_route": "browser",
            "reported_device": "Kingston USB Drive",
            "device_local_id": "kingston-usb",
            "detected": {
                "usb_vendor_id": "0x0951",
                "usb_product_id": "0x1666",
                "device_class": "mass_storage",
            },
            "identity_source": "tester_identified",
            "classification_correct": True,
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = pathlib.Path(tmpdir)
            session_file = tmp_path / "flashguard-nonandroid.json"
            session_data = self.make_session([non_android_rec])
            session_file.write_text(json.dumps(session_data, indent=2))

            res = subprocess.run(
                [sys.executable, str(DERIVE_PENDING_TOOL), str(session_file)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(res.returncode, 0)

            derived_file = tmp_path / "flashguard-nonandroid-derived.json"
            derived_data = json.loads(derived_file.read_text(encoding="utf-8"))
            self.assertEqual(derived_data["records"][0], non_android_rec)

    def test_running_twice_refuses(self):
        rec = {
            "schema_version": "0.4",
            "record_id": "test-rec-04",
            "tester": "test-tester",
            "consent_ack": True,
            "date": "2026-09-17",
            "host_platform": "windows",
            "capture_route": "adb_host",
            "reported_device": "Test Device",
            "device_local_id": "test-dev",
            "detected": {
                "usb_vendor_id": "0x18d1",
                "usb_product_id": "0x4ee2",
                "device_class": "adb",
                "android": {
                    "android_raw": "ro.product.model=Pixel 4\n",
                    "android_derivation": "pending",
                },
            },
            "identity_source": "tester_identified",
            "classification_correct": True,
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = pathlib.Path(tmpdir)
            session_file = tmp_path / "flashguard-twice.json"
            session_file.write_text(json.dumps(self.make_session([rec]), indent=2))

            res1 = subprocess.run(
                [sys.executable, str(DERIVE_PENDING_TOOL), str(session_file)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(res1.returncode, 0)

            res2 = subprocess.run(
                [sys.executable, str(DERIVE_PENDING_TOOL), str(session_file)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(res2.returncode, 1)
            self.assertIn("Refusing to overwrite", res2.stderr)

    def test_derived_file_passes_intake_where_pending_failed(self):
        props_file = ANDROID_FIXTURES / "samsung-a5-2017-android8.props"
        raw_text = "\n".join(
            line for line in props_file.read_text(encoding="utf-8").splitlines()
            if not line.startswith("#!")
        )

        rec = {
            "schema_version": "0.4",
            "record_id": "test-samsung-a5-close-loop",
            "tester": "test-tester",
            "consent_ack": True,
            "date": "2026-09-17",
            "host_platform": "windows",
            "capture_route": "adb_host",
            "reported_device": "Samsung A5",
            "device_local_id": "samsung-a5",
            "detected": {
                "usb_vendor_id": "0x04e8",
                "usb_product_id": "0x6860",
                "device_class": "adb",
                "android": {
                    "android_raw": raw_text,
                    "android_derivation": "pending",
                },
            },
            "identity_source": "tester_identified",
            "classification_correct": True,
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = pathlib.Path(tmpdir)
            session_file = tmp_path / "flashguard-session.json"
            session_file.write_text(json.dumps(self.make_session([rec]), indent=2))

            # 1. Intake must fail on pending session file and mention derive-pending.py
            r_intake_pending = subprocess.run(
                [sys.executable, str(INTAKE_TOOL), str(session_file)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(r_intake_pending.returncode, 1)
            self.assertIn("tools/derive-pending.py", r_intake_pending.stderr)

            # 2. Derive pending
            r_derive = subprocess.run(
                [sys.executable, str(DERIVE_PENDING_TOOL), str(session_file)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(r_derive.returncode, 0)

            derived_file = tmp_path / "flashguard-session-derived.json"
            self.assertTrue(derived_file.is_file())

            # 3. Intake must pass on derived session file
            r_intake_derived = subprocess.run(
                [sys.executable, str(INTAKE_TOOL), str(derived_file)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(r_intake_derived.returncode, 0, f"Intake on derived failed:\n{r_intake_derived.stderr}")
            self.assertIn("Session export checked against schema", r_intake_derived.stdout)


if __name__ == "__main__":
    unittest.main()
