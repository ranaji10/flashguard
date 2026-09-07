import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("coverage_module", ROOT / "data" / "coverage.py")
COVERAGE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(COVERAGE)


class FalseSafeGateTest(unittest.TestCase):
    def test_false_safe_exits_one(self):
        with self.assertRaises(SystemExit) as raised:
            COVERAGE.enforce_false_safe_gate([{"expected": "unsafe", "verdict": "safe"}])
        self.assertEqual(raised.exception.code, 1)


if __name__ == "__main__":
    unittest.main()
