# SPDX-License-Identifier: GPL-3.0-or-later
"""The five gaps found verifying batch 7.6, each with a test that fails without its fix."""
import copy
import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "data"))
sys.path.insert(0, str(ROOT))
import merge  # noqa: E402

# Built at runtime so the publication scan over tracked files never sees a serial-shaped string.
SN = "_S" + "N:"
import coverage  # noqa: E402


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


INTAKE = load("intake_mod", ROOT / "tools" / "intake.py")
TI = load("test_intake_mod", ROOT / "tests" / "test_intake.py")


class Residue76(unittest.TestCase):
    def test_1_report_only_runs_descriptor_privacy_even_if_scan_pii_misses(self):
        rec = copy.deepcopy(TI.get_real_spacewar_record())
        rec["record_id"] = "test-residue-1"
        rec["consent_ack"] = True
        session = {
            "kit_version": "2026-09-17", "handle": "residue", "host_platform": "ubuntu", "host_shell": "bash",
            "session_timestamp": "2026-09-24T01:00:00.000Z", "session_notes": "x",
            "manifest": {"devices_read": 1, "descriptors_count": 1, "android_fingerprints": 1},
            "records": [rec],
            "descriptors": [{"filename": "18d1-4ee2-20260924-000001.desc",
                             "content": "  product   YUPIK-QRD " + SN + "RAW7777\n"}],
        }
        saved = INTAKE.scan_pii
        INTAKE.scan_pii = lambda raw, where, problems: None   # simulate scan_pii missing it
        try:
            with tempfile.TemporaryDirectory() as tmp:
                f = pathlib.Path(tmp) / "flashguard-residue.json"
                f.write_text(json.dumps(session))
                with self.assertRaises(SystemExit) as ctx:
                    INTAKE.run_intake(f, write=False)
            self.assertIn("descriptor-privacy", str(ctx.exception.code))
        finally:
            INTAKE.scan_pii = saved

    def test_2_masked_serial_on_same_line_does_not_hide_a_raw_one(self):
        with tempfile.TemporaryDirectory() as tmp:
            pathlib.Path(tmp, "a.desc").write_text("x " + SN + "<stripped> y " + SN + "RAW12345\n")
            r = subprocess.run(["bash", str(ROOT / "tests" / "check-descriptor-privacy.sh"), tmp],
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 1, r.stdout)
            pathlib.Path(tmp, "a.desc").write_text("x " + SN + "<stripped>\nz " + SN + "<the serial>\n")
            r = subprocess.run(["bash", str(ROOT / "tests" / "check-descriptor-privacy.sh"), tmp],
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stdout)

    def test_3_scan_pii_accepts_placeholders_and_plain_notes_refuses_raw(self):
        for ok in ("YUPIK " + SN + "<stripped>", "x " + SN + "<the serial> y", "S" + "N: unknown"):
            p = []
            merge.scan_pii(ok, "t", p)
            self.assertEqual(p, [], ok)
        for bad in ("YUPIK " + SN + "ABC123", SN + "<stripped> " + SN + "REAL999"):
            p = []
            merge.scan_pii(bad, "t", p)
            self.assertTrue(p, bad)

    def test_4_intake_uses_coverage_pairing_not_a_copy(self):
        self.assertIs(INTAKE.pair_record_with_recipes.__code__, coverage.pair_record_with_recipes.__code__)
        recipe = {"target": {"product_device": "spacewar", "supported_device_codes": ["spacewar_alias"]}}
        for dev in ("SPACEWAR", "Spacewar", "spacewar_alias"):
            rec = {"detected": {"android": {"product_device": dev}}}
            self.assertEqual(len(INTAKE.pair_record_with_recipes(rec, [("r", recipe)])), 1, dev)

    def test_5_runbook_names_the_file_derive_pending_writes(self):
        tool = (ROOT / "tools" / "derive-pending.py").read_text()
        self.assertIn('f"{stem}-derived.json"', tool)
        book = (ROOT / "docs" / "reference" / "testing-runbook.md").read_text()
        self.assertIn("flashguard-sam-2026-09-22T08-25-52-959Z-derived.json", book)


if __name__ == "__main__":
    unittest.main()
