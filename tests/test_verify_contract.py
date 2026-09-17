import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from flashguard import verify


SAFE_RECIPE = {
    "schema_version": "0.1",
    "recipe_id": "oriole-system-only",
    "target": {
        "product_device": "oriole",
        "models": ["GD1YQ", "G9S9B"],
        "partition_scheme": "A/B",
    },
    "assets": [
        {
            "asset_id": "system",
            "role": "system",
            "product_device": "oriole",
        }
    ],
    "operations": [
        {"kind": "write-image", "partition": "system", "asset_id": "system"}
    ],
}


class VerifyContractTest(unittest.TestCase):
    def test_malformed_recipe_abstains_as_invalid_recipe(self):
        result = verify(
            {"product_device": "oriole", "product_model": "GD1YQ", "partition_scheme": "A/B"},
            {"schema_version": "0.1"},
        )

        self.assertEqual(result["verdict"], "cannot-verify")
        self.assertTrue(
            any("invalid recipe" in reason["message"].lower() for reason in result["reasons"])
        )

    def test_missing_fingerprint_evidence_abstains(self):
        result = verify({}, SAFE_RECIPE)

        self.assertEqual(result["verdict"], "cannot-verify")
        self.assertTrue(result["reasons"])
        self.assertIn("coverage", result)

    def test_model_mismatch_is_unsafe_not_abstention(self):
        fingerprint = {
            "product_device": "cheetah",
            "product_model": "GD1YQ",
            "partition_scheme": "A/B",
        }

        result = verify(fingerprint, SAFE_RECIPE)

        self.assertEqual(result["verdict"], "unsafe")
        self.assertTrue(result["reasons"])
        self.assertIn("coverage", result)


if __name__ == "__main__":
    unittest.main()
