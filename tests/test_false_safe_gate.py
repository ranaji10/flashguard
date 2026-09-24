import importlib.util
import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("coverage_module", ROOT / "data" / "coverage.py")
COVERAGE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(COVERAGE)

sys.path.insert(0, str(ROOT))
from flashguard import verify


class FalseSafeGateTest(unittest.TestCase):
    def test_false_safe_exits_one(self):
        with self.assertRaises(SystemExit) as raised:
            COVERAGE.enforce_false_safe_gate([{"expected": "unsafe", "verdict": "safe"}])
        self.assertEqual(raised.exception.code, 1)

    def test_avicii_shape_false_safe_exits_one(self):
        """A run with expected cannot-verify, human_assessment unsafe, verdict safe fails the gate."""
        with self.assertRaises(SystemExit) as raised:
            COVERAGE.enforce_false_safe_gate([{"expected": "cannot-verify", "human_assessment": "unsafe", "verdict": "safe"}])
        self.assertEqual(raised.exception.code, 1)

    def test_decided_share_below_floor_exits_one(self):
        """A decided share below the floor fails the build."""
        runs = [
            {"paired": True, "verdict": "cannot-verify", "expected": "cannot-verify", "human_assessment": "cannot-verify"}
        ]
        with self.assertRaises(SystemExit) as raised:
            COVERAGE.enforce_verifier_gate(runs, floor_data={"decided_over_paired": 0.5})
        self.assertEqual(raised.exception.code, 1)

    def test_avicii_shaped_recipe_labelled_unsafe_is_not_safe(self):
        """avicii was relabelled safe on 24 Sep. The shape that once shipped a false safe stays guarded:
        the same recipe labelled unsafe, with its unlock step unclassified, must never return safe."""
        recipe_path = ROOT / "data" / "recipes-v0.2" / "avicii.json"
        with open(recipe_path, encoding="utf-8") as fh:
            recipe = json.load(fh)
        recipe["human_assessment"] = "unsafe"
        recipe["prerequisites"]["bootloader_state"].pop("unlock_class", None)
        recipe["prerequisites"]["bootloader_state"].pop("unlock_step", None)
        target = recipe["target"]
        fp = {
            "product_device": target["product_device"],
            "product_model": target["models"][0],
            "partition_scheme": target.get("partition_scheme"),
            "bootloader_state": "unlocked",
            "android_version": 12,
        }
        result = verify(fp, recipe)
        self.assertNotEqual(result["verdict"], "safe",
                            "an avicii-shaped recipe with an unclassified unlock must not return safe")

if __name__ == "__main__":
    unittest.main()
