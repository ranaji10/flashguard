import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from flashguard import verify


BASE_RECIPE = {
    "schema_version": "0.2",
    "recipe_id": "spacewar-unlock-aware",
    "source": {
        "device_facts_from": "synthetic",
        "consulted": "2026-09-08",
        "authored": "independent",
    },
    "target": {
        "product_device": "spacewar",
        "partition_scheme": "virtual_A/B",
    },
    "install_method": "fastboot_nexus",
    "prerequisites": {
        "bootloader_unlocked": {
            "state": "OPEN",
            "required": "unlocked",
            "declared_by": "unlock_bootloader",
            "source_evidence": "synthetic config unlock step",
        }
    },
    "operations": [{"kind": "write-image", "partition": "system"}],
    "source_fields_unused": [],
}


def fingerprint(bootloader_state=None, product_device="spacewar"):
    result = {
        "product_device": product_device,
        "partition_scheme": "virtual_A/B",
    }
    if bootloader_state is not None:
        result["bootloader_unlocked"] = bootloader_state
    return result


class VerifyV2Test(unittest.TestCase):
    def test_matching_prerequisite_is_safe(self):
        result = verify(fingerprint("unlocked"), BASE_RECIPE)
        self.assertEqual(result["verdict"], "safe")

    def test_locked_prerequisite_is_unsafe(self):
        result = verify(fingerprint("locked"), BASE_RECIPE)
        self.assertEqual(result["verdict"], "unsafe")

    def test_missing_prerequisite_evidence_abstains(self):
        result = verify(fingerprint(), BASE_RECIPE)
        self.assertEqual(result["verdict"], "cannot-verify")
        self.assertIn("bootloader_unlocked", str(result["reasons"]))

    def test_minimum_version_below_requirement_is_unsafe(self):
        recipe = dict(BASE_RECIPE)
        recipe["prerequisites"] = {
            "android_version": {
                "state": "OPEN",
                "required": 12,
                "declared_by": "requirements.android",
                "source_evidence": "synthetic config requirement",
            }
        }
        result = verify(dict(fingerprint("unlocked"), android_version=11), recipe)
        self.assertEqual(result["verdict"], "unsafe")

    def test_v01_without_prerequisites_still_abstains(self):
        recipe = {
            "schema_version": "0.1",
            "recipe_id": "legacy",
            "target": {"product_device": "spacewar", "variant": "x", "partition_scheme": "virtual_A/B"},
            "assets": [],
            "operations": [],
        }
        self.assertEqual(verify(fingerprint("unlocked"), recipe)["verdict"], "cannot-verify")

    def test_identity_mismatch_precedes_prerequisite_reasoning(self):
        result = verify(fingerprint("locked", "other-device"), BASE_RECIPE)
        self.assertEqual(result["verdict"], "unsafe")
        self.assertIn("device-mismatch", str(result["reasons"]))

    def test_partial_real_samsung_fingerprint_cannot_satisfy_unlock(self):
        result = verify(
            {"product_device": "a5y17lte", "partition_scheme": "unknown"},
            dict(BASE_RECIPE, target={"product_device": "a5y17lte", "partition_scheme": "unknown"}),
        )
        self.assertEqual(result["verdict"], "cannot-verify")
        self.assertIn("bootloader_unlocked", str(result["reasons"]))

    def test_prerequisite_presence_states_are_distinct(self):
        absent = dict(BASE_RECIPE)
        absent.pop("prerequisites")
        declared_none = dict(BASE_RECIPE, prerequisites={})
        author_unknown = dict(BASE_RECIPE, prerequisites=None)
        self.assertNotEqual(verify(fingerprint("unlocked"), absent)["reasons"], verify(fingerprint("unlocked"), declared_none)["reasons"])
        self.assertNotEqual(verify(fingerprint("unlocked"), declared_none)["reasons"], verify(fingerprint("unlocked"), author_unknown)["reasons"])


if __name__ == "__main__":
    unittest.main()
