# SPDX-License-Identifier: GPL-3.0-or-later
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class ContributionsValidationTest(unittest.TestCase):
    def test_pending_record_refused_at_matrix_boundary(self):
        """A record with android_derivation: pending must be rejected at the matrix boundary."""
        pending_record = {
            "schema_version": "0.4",
            "record_id": "test-pending-1234",
            "tester": "test-tester",
            "consent_ack": True,
            "date": "2026-09-16",
            "host_platform": "windows",
            "capture_route": "adb_host",
            "reported_device": "Test Phone",
            "device_local_id": "test-phone",
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
            contrib_dir = tmp_path / "contributions"
            contrib_dir.mkdir()
            test_file = contrib_dir / "test-pending.jsonl"
            test_file.write_text(json.dumps(pending_record) + "\n")

            code = f"""
import sys, pathlib
import merge
merge.CONTRIB = pathlib.Path({repr(str(contrib_dir))})
merge.OUT = pathlib.Path({repr(str(tmp_path / 'device-matrix.jsonl'))})
sys.argv = ['merge.py', '--check']
sys.exit(merge.main())
"""
            res = subprocess.run(
                [sys.executable, "-c", code],
                cwd=str(ROOT / "data"),
                capture_output=True,
                text=True,
            )
            self.assertEqual(res.returncode, 1, "pending record must exit with 1")
            self.assertIn("android_derivation is pending -- derivation has not been run", res.stdout)

    def test_completed_record_accepted(self):
        """A completed record with derived android block must be accepted."""
        completed_record = {
            "schema_version": "0.4",
            "record_id": "test-completed-1234",
            "tester": "test-tester",
            "consent_ack": True,
            "date": "2026-09-16",
            "host_platform": "macos",
            "capture_route": "adb_host",
            "reported_device": "Test Phone",
            "device_local_id": "test-phone",
            "detected": {
                "usb_vendor_id": "0x18d1",
                "usb_product_id": "0x4ee2",
                "device_class": "adb",
                "android": {
                    "product_model": "Pixel 4",
                    "partition_scheme": "virtual_A/B",
                },
            },
            "identity_source": "tester_identified",
            "classification_correct": True,
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = pathlib.Path(tmpdir)
            contrib_dir = tmp_path / "contributions"
            contrib_dir.mkdir()
            test_file = contrib_dir / "test-completed.jsonl"
            test_file.write_text(json.dumps(completed_record) + "\n")

            code = f"""
import sys, pathlib
import merge
merge.CONTRIB = pathlib.Path({repr(str(contrib_dir))})
merge.OUT = pathlib.Path({repr(str(tmp_path / 'device-matrix.jsonl'))})
sys.argv = ['merge.py', '--check']
sys.exit(merge.main())
"""
            res = subprocess.run(
                [sys.executable, "-c", code],
                cwd=str(ROOT / "data"),
                capture_output=True,
                text=True,
            )
            self.assertEqual(res.returncode, 0, "completed record must exit with 0")


if __name__ == "__main__":
    unittest.main()
