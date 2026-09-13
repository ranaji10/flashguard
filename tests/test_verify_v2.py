import copy
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

    def test_exact_variant_match_gives_definite_verdict(self):
        recipe = dict(BASE_RECIPE, target={"product_device": "spacewar", "variant": "global", "partition_scheme": "virtual_A/B"})
        fp = dict(fingerprint("unlocked"), variant="global")
        result = verify(fp, recipe)
        self.assertEqual(result["verdict"], "safe")

    def test_supported_device_codes_alias_gives_definite_verdict_with_alias_named(self):
        recipe = dict(
            BASE_RECIPE,
            target={
                "product_device": "spacewar",
                "variant": "global",
                "partition_scheme": "virtual_A/B",
                "supported_device_codes": ["spacewar-eea", "spacewar-in"],
            },
        )
        fp = dict(fingerprint("unlocked", product_device="spacewar-eea"), variant="spacewar-eea")
        result = verify(fp, recipe)
        self.assertEqual(result["verdict"], "safe")
        self.assertTrue(
            any(
                reason.get("code") == "match-device-alias" and "spacewar-eea" in reason.get("message", "")
                for reason in result["reasons"]
            )
        )

    def test_unconfirmed_variant_with_agreeing_partition_and_bootloader_abstains_naming_variant(self):
        recipe = dict(BASE_RECIPE, target={"product_device": "spacewar", "variant": "global", "partition_scheme": "virtual_A/B"})
        fp = fingerprint("unlocked")
        result = verify(fp, recipe)
        self.assertEqual(result["verdict"], "cannot-verify")
        self.assertNotEqual(result["verdict"], "safe")
        self.assertTrue(
            any(
                reason.get("code") == "missing-variant" or "variant" in reason.get("fields", [])
                for reason in result["reasons"]
                if reason.get("result") == "abstain"
            )
        )

    def test_human_confirmed_variant_treated_as_exact_and_records_human_provenance(self):
        recipe = dict(BASE_RECIPE, target={"product_device": "spacewar", "variant": "global", "partition_scheme": "virtual_A/B"})
        fp = dict(fingerprint("unlocked"), variant="global", variant_source="human")
        result = verify(fp, recipe)
        self.assertEqual(result["verdict"], "safe")
        self.assertTrue(
            any(
                "human" in reason.get("message", "").lower() or reason.get("code") == "match-variant-human-confirmed"
                for reason in result["reasons"]
            )
        )

    def test_definite_verdict_carries_record_id_timestamp_and_consumed_fields(self):
        fp = {
            "record_id": "rec-001",
            "capture_timestamp": "2026-09-08",
            "product_device": "spacewar",
            "partition_scheme": "virtual_A/B",
            "bootloader_unlocked": "unlocked",
        }
        result = verify(fp, BASE_RECIPE)
        self.assertEqual(result["verdict"], "safe")
        self.assertIn("evidence", result)
        self.assertEqual(result["evidence"]["record_id"], "rec-001")
        self.assertEqual(result["evidence"]["capture_timestamp"], "2026-09-08")
        self.assertTrue(
            {"product_device", "partition_scheme", "bootloader_unlocked"}.issubset(
                set(result["evidence"]["fields_consumed"])
            )
        )



    def test_alias_device_code_does_not_confirm_an_unknown_variant(self):
        """The branch that shipped a false safe on 13 September.

        An unknown variant recorded NO reason at all when the device code appeared in
        supported_device_codes -- a bare `pass`. It contributed nothing, everything else
        passed, and the verdict came out SAFE while fields_consumed still claimed the
        variant had been consumed, so the evidence said it was checked.

        The sibling test passes because its fingerprint device code is not an alias, so it
        never enters this branch. A test that passes for the case it happens to construct
        is not coverage of the case it is named after.
        """
        recipe = copy.deepcopy(BASE_RECIPE)
        recipe["target"]["variant"] = "spacewar"
        recipe["target"]["supported_device_codes"] = ["spacewar"]

        fp = fingerprint("unlocked")
        fp["variant"] = "unknown"
        fp["record_id"] = "alias-unknown-variant"
        fp["capture_timestamp"] = "2026-09-13T00:00:00Z"

        result = verify(fp, recipe)
        self.assertNotEqual(result["verdict"], "safe",
                            "an unconfirmed variant must never reach safe, alias or not")
        self.assertEqual(result["verdict"], "cannot-verify")
        self.assertIn("missing-variant", [r["code"] for r in result["reasons"]],
                      "an unconfirmed variant must record a reason, not be swallowed")


if __name__ == "__main__":
    unittest.main()
