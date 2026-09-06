import unittest

from flashguard import verify


SAFE_RECIPE = {
    "schema_version": "0.1",
    "recipe_id": "oriole-system-only",
    "target": {
        "product_device": "oriole",
        "variant": "global",
        "partition_scheme": "A/B",
    },
    "assets": [
        {
            "asset_id": "system",
            "role": "system",
            "product_device": "oriole",
            "variant": "global",
        }
    ],
    "operations": [
        {"kind": "write-image", "partition": "system", "asset_id": "system"}
    ],
}


class VerifyContractTest(unittest.TestCase):
    def test_missing_fingerprint_evidence_abstains(self):
        result = verify({}, SAFE_RECIPE)

        self.assertEqual(result["verdict"], "cannot-verify")
        self.assertTrue(result["reasons"])
        self.assertIn("coverage", result)

    def test_model_mismatch_is_unsafe_not_abstention(self):
        fingerprint = {
            "product_device": "cheetah",
            "variant": "global",
            "partition_scheme": "A/B",
        }

        result = verify(fingerprint, SAFE_RECIPE)

        self.assertEqual(result["verdict"], "unsafe")
        self.assertTrue(result["reasons"])
        self.assertIn("coverage", result)


if __name__ == "__main__":
    unittest.main()
