import copy
import json
import pathlib
import re
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
        "upstream_untested": "unestablished",
    },
    "target": {
        "product_device": "spacewar",
        "models": ["A063"],
        "partition_scheme": "virtual_A/B",
    },
    "install_method": "fastboot_nexus",
    "prerequisites": {
        "bootloader_state": {
            "state": "OPEN",
            "required": "unlocked",
            "unlock_class": "command",
            "unlock_step": True,
            "declared_by": "unlock_bootloader",
            "source_evidence": "synthetic config unlock step",
        }
    },
    "operations": [{"kind": "write-image", "partition": "system"}],
    "source_fields_unused": [],
}


def fingerprint(bootloader_state=None, product_device="spacewar", product_model="A063"):
    result = {
        "product_device": product_device,
        "product_model": product_model,
        "partition_scheme": "virtual_A/B",
    }
    if bootloader_state is not None:
        result["bootloader_state"] = bootloader_state
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
        self.assertIn("bootloader_state", str(result["reasons"]))

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
            "target": {"product_device": "spacewar", "models": ["A063"], "partition_scheme": "virtual_A/B"},
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
            {"product_device": "a5y17lte", "product_model": "SM-A520F", "partition_scheme": "unknown"},
            dict(BASE_RECIPE, target={"product_device": "a5y17lte", "models": ["SM-A520F"], "partition_scheme": "unknown"}),
        )
        self.assertEqual(result["verdict"], "cannot-verify")
        self.assertIn("bootloader_state", str(result["reasons"]))

    def test_prerequisite_presence_states_are_distinct(self):
        absent = dict(BASE_RECIPE)
        absent.pop("prerequisites")
        declared_none = dict(BASE_RECIPE, prerequisites={})
        author_unknown = dict(BASE_RECIPE, prerequisites=None)
        self.assertNotEqual(verify(fingerprint("unlocked"), absent)["reasons"], verify(fingerprint("unlocked"), declared_none)["reasons"])
        self.assertNotEqual(verify(fingerprint("unlocked"), declared_none)["reasons"], verify(fingerprint("unlocked"), author_unknown)["reasons"])

    def test_exact_model_match_gives_safe_verdict(self):
        recipe = dict(BASE_RECIPE, target={"product_device": "spacewar", "models": ["A063"], "partition_scheme": "virtual_A/B"})
        fp = fingerprint("unlocked", product_model="A063")
        result = verify(fp, recipe)
        self.assertEqual(result["verdict"], "safe")
        self.assertTrue(any(r["code"] == "match-product_model" for r in result["reasons"]))

    def test_model_not_in_allowlist_returns_unsafe(self):
        """A fingerprint whose codename matches and whose model is not in the list returns unsafe."""
        recipe = {
            "schema_version": "0.2",
            "recipe_id": "a5xelte-recovery-v2",
            "source": {"device_facts_from": "synthetic", "consulted": "2026-09-16", "authored": "independent", "upstream_untested": "unestablished"},
            "target": {
                "product_device": "a5xelte",
                "models": ["SM-A510F"],
                "partition_scheme": "single",
            },
            "install_method": "heimdall_flash_recovery",
            "prerequisites": {
                "bootloader_state": {
                    "state": "OPEN",
                    "required": "unlocked",
                    "unlock_class": "command",
                    "unlock_step": True,
                    "declared_by": "unlock_bootloader",
                    "source_evidence": "synthetic config unlock step",
                }
            },
            "operations": [{"kind": "write-image", "partition": "recovery"}],
            "source_fields_unused": [],
        }
        fp = {
            "product_device": "a5xelte",
            "product_model": "SM-A510M",
            "partition_scheme": "single",
            "bootloader_state": "unlocked",
        }
        result = verify(fp, recipe)
        self.assertEqual(result["verdict"], "unsafe", "A model outside the allowlist must return unsafe.")
        codes = [r["code"] for r in result["reasons"]]
        self.assertIn("model-mismatch", codes)

    def test_absent_or_unknown_product_model_abstains_and_does_not_return_unsafe(self):
        """A fingerprint with product_model absent or unknown abstains, not unsafe."""
        for missing_val in (None, "", "unknown", "not_applicable"):
            fp = fingerprint("unlocked")
            if missing_val is None:
                del fp["product_model"]
            else:
                fp["product_model"] = missing_val
            result = verify(fp, BASE_RECIPE)
            self.assertEqual(result["verdict"], "cannot-verify", f"Missing product_model ({missing_val}) must abstain, not return unsafe.")
            codes = [r["code"] for r in result["reasons"]]
            self.assertIn("missing-product_model", codes)
            self.assertNotIn("model-mismatch", codes)

    def test_recipe_with_no_model_list_abstains(self):
        """A recipe with no model list (or empty list) abstains and does not pass."""
        for empty_models in (None, []):
            recipe = copy.deepcopy(BASE_RECIPE)
            if empty_models is None:
                del recipe["target"]["models"]
            else:
                recipe["target"]["models"] = empty_models
            result = verify(fingerprint("unlocked"), recipe)
            self.assertEqual(result["verdict"], "cannot-verify")
            codes = [r["code"] for r in result["reasons"]]
            self.assertIn("models-unestablished", codes)

    def test_supported_device_codes_alias_gives_definite_verdict_with_alias_named(self):
        recipe = dict(
            BASE_RECIPE,
            target={
                "product_device": "spacewar",
                "models": ["A063"],
                "partition_scheme": "virtual_A/B",
                "supported_device_codes": ["spacewar-eea", "spacewar-in"],
            },
        )
        fp = dict(fingerprint("unlocked", product_device="spacewar-eea", product_model="A063"))
        result = verify(fp, recipe)
        self.assertEqual(result["verdict"], "safe")
        self.assertTrue(
            any(
                reason.get("code") == "match-device-alias" and "spacewar-eea" in reason.get("message", "")
                for reason in result["reasons"]
            )
        )

    def test_definite_verdict_carries_record_id_timestamp_and_consumed_fields(self):
        fp = {
            "record_id": "rec-001",
            "capture_timestamp": "2026-09-08",
            "product_device": "spacewar",
            "product_model": "A063",
            "partition_scheme": "virtual_A/B",
            "bootloader_state": "unlocked",
        }
        result = verify(fp, BASE_RECIPE)
        self.assertEqual(result["verdict"], "safe")
        self.assertIn("evidence", result)
        self.assertEqual(result["evidence"]["record_id"], "rec-001")
        self.assertEqual(result["evidence"]["capture_timestamp"], "2026-09-08")
        self.assertTrue(
            {"product_device", "product_model", "partition_scheme", "bootloader_state"}.issubset(
                set(result["evidence"]["fields_consumed"])
            )
        )

    def test_v01_asset_product_device_mismatch_returns_unsafe(self):
        """v0.1 asset identity mismatch against target.product_device returns unsafe."""
        recipe = {
            "schema_version": "0.1",
            "recipe_id": "oriole-system-only",
            "target": {
                "product_device": "oriole",
                "models": ["GD1YQ"],
                "partition_scheme": "A/B",
            },
            "assets": [
                {
                    "asset_id": "system",
                    "role": "system",
                    "product_device": "raven",
                }
            ],
            "operations": [
                {"kind": "write-image", "partition": "system", "asset_id": "system"}
            ],
        }
        fp = {
            "product_device": "oriole",
            "product_model": "GD1YQ",
            "partition_scheme": "A/B",
        }
        result = verify(fp, recipe)
        self.assertEqual(result["verdict"], "unsafe")
        codes = [r["code"] for r in result["reasons"]]
        self.assertIn("asset-product_device-mismatch", codes)


class StateIsNotRead(unittest.TestCase):
    """`state` is carried on every prerequisite and must never reach a verdict.

    AUTHORISED BY RANAJI, 13 September, as the cheap half of a decision he deferred.
    The question was whether to drop `state` or wait for upstream to give it a meaning.
    The dangerous answer is neither: a field that is PRESENT, unvalidated and unread is
    worse than one that is absent, because the day something starts trusting it there is
    no test that notices. This is that test. With it, keeping the field costs nothing and
    waiting for upstream is free.

    It is deliberately BEHAVIOURAL rather than a grep of the source. A grep proves the
    string does not appear; this proves the value does not matter. Those are different
    claims, and only the second one survives a refactor.
    """

    def _mutate_state(self, recipe, value):
        out = copy.deepcopy(recipe)
        for name, pre in (out.get("prerequisites") or {}).items():
            if isinstance(pre, dict) and "state" in pre:
                pre["state"] = value
        return out

    def test_state_value_cannot_change_a_verdict(self):
        """Same recipe, four different `state` values, one identical answer each time."""
        for recipe_name, recipe in (("locked-bootloader", BASE_RECIPE),):
            for fp_state in ("locked", "unlocked"):
                fp = fingerprint(fp_state)
                fp["record_id"] = "state-invariance"
                fp["capture_timestamp"] = "2026-09-13T00:00:00Z"
                baseline = verify(fp, recipe)
                for planted in ("CLOSED", "SATISFIED", "", None):
                    other = verify(fp, self._mutate_state(recipe, planted))
                    self.assertEqual(
                        other["verdict"], baseline["verdict"],
                        "%s/%s: setting state=%r changed the verdict. Something reads "
                        "`state`, and nothing is allowed to." % (recipe_name, fp_state, planted))
                    self.assertEqual(
                        [r["code"] for r in other["reasons"]],
                        [r["code"] for r in baseline["reasons"]],
                        "%s/%s: setting state=%r changed the reasons. `state` is "
                        "provenance, not evidence." % (recipe_name, fp_state, planted))

    def test_state_is_never_named_in_the_evidence(self):
        """fields_consumed is what an auditor reads. It must not claim `state` was used.

        The evidence stamp must never assert unread provenance fields were consumed.
        """
        fp = fingerprint("unlocked")
        fp["record_id"] = "state-evidence"
        fp["capture_timestamp"] = "2026-09-13T00:00:00Z"
        consumed = verify(fp, BASE_RECIPE).get("fields_consumed") or []
        named = [f for f in consumed if "state" in str(f).split(".")]
        self.assertEqual(named, [],
                         "fields_consumed names `state` (%r). Either the verifier reads it, "
                         "which is forbidden, or the stamp is claiming a check that did not "
                         "happen, which is worse." % (named,))


class UnlockOutOfBandTest(unittest.TestCase):
    """Prerequisites that cannot be established from device state (out-of-band unlock)."""

    def _oob_recipe(self, method="fastboot_fairphone", unlock_class="out_of_band"):
        recipe = copy.deepcopy(BASE_RECIPE)
        recipe["prerequisites"] = {
            "bootloader_state": {
                "state": "OPEN",
                "required": "unlocked",
                "unlock_class": unlock_class,
                "unlock_method": method,
                "unlock_step": True,
                "declared_by": "unlock_bootloader",
                "source_evidence": "synthetic oob unlock",
            }
        }
        return recipe

    def test_out_of_band_unlock_abstains_with_unlock_out_of_band_and_no_fingerprint(self):
        recipe = self._oob_recipe("fastboot_fairphone")
        for fp in (None, {}, fingerprint()):
            result = verify(fp, recipe)
            self.assertEqual(result["verdict"], "cannot-verify")
            codes = [r["code"] for r in result["reasons"]]
            self.assertIn("unlock-out-of-band", codes)
            oob_reasons = [r for r in result["reasons"] if r["code"] == "unlock-out-of-band"]
            self.assertTrue(all(r["result"] == "abstain" for r in oob_reasons))
            self.assertIn("guidance", result["evidence"])
            self.assertTrue(len(result["evidence"]["guidance"]["steps"]) > 0)

    def test_command_unlock_never_returns_unlock_out_of_band(self):
        recipe = self._oob_recipe("fastboot_nexus", unlock_class="command")
        for fp in (None, {}, fingerprint(), fingerprint("unlocked"), fingerprint("locked")):
            result = verify(fp, recipe)
            codes = [r["code"] for r in result["reasons"]]
            self.assertNotIn("unlock-out-of-band", codes,
                             "command unlock must never return unlock-out-of-band")
        # Fingerprint confirming unlock on command-class recipe yields safe
        safe_result = verify(fingerprint("unlocked"), recipe)
        self.assertEqual(safe_result["verdict"], "safe")

    def test_omitted_unlock_class_returns_missing_bootloader_and_not_unlock_out_of_band(self):
        recipe = copy.deepcopy(BASE_RECIPE)
        del recipe["prerequisites"]["bootloader_state"]["unlock_class"]
        # The fingerprint MATCHES the required state. If omission were ever read as
        # "command", this would verify clean and return safe. It must not: absence of
        # unlock_class abstains regardless of what the device reports.
        result = verify(fingerprint("unlocked"), recipe)
        self.assertEqual(result["verdict"], "cannot-verify")
        codes = [r["code"] for r in result["reasons"]]
        self.assertIn("unlock-class-undeclared", codes)
        self.assertNotIn("unlock-out-of-band", codes)

    def test_guidance_for_known_method_present_and_for_unknown_absent(self):
        known_recipe = self._oob_recipe("fastboot_sony")
        known_result = verify(None, known_recipe)
        self.assertIn("guidance", known_result["evidence"])
        self.assertIn("steps", known_result["evidence"]["guidance"])
        self.assertIn("link", known_result["evidence"]["guidance"])

        unknown_recipe = self._oob_recipe("fastboot_obscure_unknown_vendor")
        unknown_result = verify(None, unknown_recipe)
        self.assertNotIn("guidance", unknown_result["evidence"],
                         "guidance for unknown method must be absent rather than empty or invented")


class UpstreamUntestedGateTest(unittest.TestCase):
    """A recipe derived from an upstream config marked untested must never reach safe."""

    def test_untested_recipe_cannot_reach_safe_even_with_confirmed_prerequisites(self):
        """Build a fingerprint that would otherwise produce safe and assert it does not."""
        recipe = copy.deepcopy(BASE_RECIPE)
        recipe["source"]["upstream_untested"] = True

        fp = fingerprint("unlocked")
        result = verify(fp, recipe)
        self.assertNotEqual(result["verdict"], "safe",
                            "a recipe marked untested by upstream must never reach safe")
        self.assertEqual(result["verdict"], "cannot-verify")
        codes = [r["code"] for r in result["reasons"]]
        self.assertIn("recipe-untested-upstream", codes)

        untested_reasons = [r for r in result["reasons"] if r["code"] == "recipe-untested-upstream"]
        self.assertEqual(len(untested_reasons), 1)
        self.assertEqual(untested_reasons[0]["result"], "abstain")
        self.assertIn("source.upstream_untested", untested_reasons[0]["fields"])

    def test_untested_string_value_also_triggers_gate(self):
        recipe = copy.deepcopy(BASE_RECIPE)
        recipe["source"]["upstream_untested"] = "untested"
        result = verify(fingerprint("unlocked"), recipe)
        self.assertEqual(result["verdict"], "cannot-verify")
        self.assertIn("recipe-untested-upstream", [r["code"] for r in result["reasons"]])

    def test_unrecognized_upstream_untested_value_abstains_with_recipe_defect_reason(self):
        """Values outside permitted (False, unestablished, None) and untested trigger recipe defect."""
        for bad_val in ("marked", "yes", "True", 123):
            recipe = copy.deepcopy(BASE_RECIPE)
            recipe["source"]["upstream_untested"] = bad_val
            result = verify(fingerprint("unlocked"), recipe)
            self.assertEqual(result["verdict"], "cannot-verify")
            codes = [r["code"] for r in result["reasons"]]
            self.assertIn("recipe-untested-unrecognized", codes)

    def test_not_untested_recipe_returns_byte_identical_reasons(self):
        """A recipe marked not-untested returns safe with confirmed prerequisites."""
        baseline_recipe = copy.deepcopy(BASE_RECIPE)
        baseline_result = verify(fingerprint("unlocked"), baseline_recipe)
        self.assertEqual(baseline_result["verdict"], "safe")

        tested_recipe = copy.deepcopy(BASE_RECIPE)
        tested_recipe["source"]["upstream_untested"] = False
        result = verify(fingerprint("unlocked"), tested_recipe)
        self.assertEqual(result["verdict"], "safe")
        self.assertEqual(
            result["reasons"], baseline_result["reasons"],
            "reasons must be byte-identical when recipe is not marked untested",
        )

    def test_absent_upstream_untested_returns_byte_identical_reasons(self):
        """A recipe with the field absent or unestablished returns safe with confirmed prerequisites."""
        baseline_recipe = copy.deepcopy(BASE_RECIPE)
        baseline_result = verify(fingerprint("unlocked"), baseline_recipe)

        for unestablished_val in ("unestablished", None):
            recipe = copy.deepcopy(BASE_RECIPE)
            recipe["source"]["upstream_untested"] = unestablished_val
            result = verify(fingerprint("unlocked"), recipe)
            self.assertEqual(result["verdict"], baseline_result["verdict"])
            self.assertEqual(
                result["reasons"], baseline_result["reasons"],
                "reasons must be byte-identical when upstream untested field is absent/unestablished",
            )

    def test_untested_recipe_with_hardware_mismatch_is_still_unsafe(self):
        """unsafe > cannot-verify: a contradicting fingerprint is still unsafe."""
        recipe = copy.deepcopy(BASE_RECIPE)
        recipe["source"]["upstream_untested"] = True

        result = verify(fingerprint("locked"), recipe)
        self.assertEqual(result["verdict"], "unsafe")
        self.assertIn("prerequisite-bootloader_state-mismatch", [r["code"] for r in result["reasons"]])

    def test_upstream_untested_field_never_named_in_fields_consumed(self):
        """fields_consumed is for fingerprint evidence only, never recipe provenance."""
        recipe = copy.deepcopy(BASE_RECIPE)
        recipe["source"]["upstream_untested"] = True

        fp = fingerprint("unlocked")
        fp["record_id"] = "untested-evidence-test"
        result = verify(fp, recipe)
        consumed = result.get("evidence", {}).get("fields_consumed", [])
        for f in consumed:
            self.assertNotIn("source", str(f))
            self.assertNotIn("upstream_untested", str(f))


import copy
import importlib.util
import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from flashguard import verify

SPEC_CHECK = importlib.util.spec_from_file_location("check_recipes_module", ROOT / "tests" / "check-recipes.py")
CHECK_RECIPES = importlib.util.module_from_spec(SPEC_CHECK)
SPEC_CHECK.loader.exec_module(CHECK_RECIPES)


BASE_RECIPE = {
    "schema_version": "0.2",
    "recipe_id": "spacewar-unlock-aware",
    "source": {
        "device_facts_from": "synthetic",
        "consulted": "2026-09-08",
        "authored": "independent",
        "upstream_untested": "unestablished",
    },
    "target": {
        "product_device": "spacewar",
        "models": ["A063"],
        "partition_scheme": "virtual_A/B",
    },
    "install_method": "fastboot_nexus",
    "prerequisites": {
        "bootloader_state": {
            "state": "OPEN",
            "required": "unlocked",
            "unlock_class": "command",
            "unlock_step": True,
            "declared_by": "unlock_bootloader",
            "source_evidence": "synthetic config unlock step",
        }
    },
    "operations": [{"kind": "write-image", "partition": "system"}],
    "source_fields_unused": [],
}


def fingerprint(bootloader_state=None, product_device="spacewar", product_model="A063"):
    result = {
        "product_device": product_device,
        "product_model": product_model,
        "partition_scheme": "virtual_A/B",
    }
    if bootloader_state is not None:
        result["bootloader_state"] = bootloader_state
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
        self.assertIn("bootloader_state", str(result["reasons"]))

    def test_minimum_version_below_requirement_is_unsafe(self):
        recipe = copy.deepcopy(BASE_RECIPE)
        recipe["prerequisites"]["android_version"] = {
            "state": "OPEN",
            "required": 12,
            "compare": "minimum",
            "declared_by": "requirements.android",
            "source_evidence": "synthetic config requirement",
        }
        result = verify(dict(fingerprint("unlocked"), android_version=11), recipe)
        self.assertEqual(result["verdict"], "unsafe")
        codes = [r["code"] for r in result["reasons"]]
        self.assertIn("prerequisite-android_version-below-minimum", codes)

    def test_v01_without_prerequisites_still_abstains(self):
        recipe = {
            "schema_version": "0.1",
            "recipe_id": "legacy",
            "target": {"product_device": "spacewar", "models": ["A063"], "partition_scheme": "virtual_A/B"},
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
            {"product_device": "a5y17lte", "product_model": "SM-A520F", "partition_scheme": "unknown"},
            dict(BASE_RECIPE, target={"product_device": "a5y17lte", "models": ["SM-A520F"], "partition_scheme": "unknown"}),
        )
        self.assertEqual(result["verdict"], "cannot-verify")
        self.assertIn("bootloader_state", str(result["reasons"]))

    def test_prerequisite_presence_states_are_distinct(self):
        absent = dict(BASE_RECIPE)
        absent.pop("prerequisites")
        declared_none = dict(BASE_RECIPE, prerequisites={})
        author_unknown = dict(BASE_RECIPE, prerequisites=None)
        self.assertNotEqual(verify(fingerprint("unlocked"), absent)["reasons"], verify(fingerprint("unlocked"), declared_none)["reasons"])
        self.assertNotEqual(verify(fingerprint("unlocked"), declared_none)["reasons"], verify(fingerprint("unlocked"), author_unknown)["reasons"])

    def test_exact_model_match_gives_safe_verdict(self):
        recipe = dict(BASE_RECIPE, target={"product_device": "spacewar", "models": ["A063"], "partition_scheme": "virtual_A/B"})
        fp = fingerprint("unlocked", product_model="A063")
        result = verify(fp, recipe)
        self.assertEqual(result["verdict"], "safe")
        self.assertTrue(any(r["code"] == "match-product_model" for r in result["reasons"]))

    def test_model_not_in_allowlist_returns_unsafe(self):
        """A fingerprint whose codename matches and whose model is not in the list returns unsafe."""
        recipe = {
            "schema_version": "0.2",
            "recipe_id": "a5xelte-recovery-v2",
            "source": {"device_facts_from": "synthetic", "consulted": "2026-09-16", "authored": "independent", "upstream_untested": "unestablished"},
            "target": {
                "product_device": "a5xelte",
                "models": ["SM-A510F"],
                "partition_scheme": "single",
            },
            "install_method": "heimdall_flash_recovery",
            "prerequisites": {
                "bootloader_state": {
                    "state": "OPEN",
                    "required": "unlocked",
                    "unlock_class": "command",
                    "unlock_step": True,
                    "declared_by": "unlock_bootloader",
                    "source_evidence": "synthetic config unlock step",
                }
            },
            "operations": [{"kind": "write-image", "partition": "recovery"}],
            "source_fields_unused": [],
        }
        fp = {
            "product_device": "a5xelte",
            "product_model": "SM-A510M",
            "partition_scheme": "single",
            "bootloader_state": "unlocked",
        }
        result = verify(fp, recipe)
        self.assertEqual(result["verdict"], "unsafe", "A model outside the allowlist must return unsafe.")
        codes = [r["code"] for r in result["reasons"]]
        self.assertIn("model-mismatch", codes)

    def test_absent_or_unknown_product_model_abstains_and_does_not_return_unsafe(self):
        """A fingerprint with product_model absent or unknown abstains, not unsafe."""
        for missing_val in (None, "", "unknown", "not_applicable"):
            fp = fingerprint("unlocked")
            if missing_val is None:
                del fp["product_model"]
            else:
                fp["product_model"] = missing_val
            result = verify(fp, BASE_RECIPE)
            self.assertEqual(result["verdict"], "cannot-verify", f"Missing product_model ({missing_val}) must abstain, not return unsafe.")
            codes = [r["code"] for r in result["reasons"]]
            self.assertIn("missing-product_model", codes)
            self.assertNotIn("model-mismatch", codes)

    def test_recipe_with_no_model_list_abstains(self):
        """A recipe with no model list (or empty list) abstains and does not pass."""
        for empty_models in (None, []):
            recipe = copy.deepcopy(BASE_RECIPE)
            if empty_models is None:
                del recipe["target"]["models"]
            else:
                recipe["target"]["models"] = empty_models
            result = verify(fingerprint("unlocked"), recipe)
            self.assertEqual(result["verdict"], "cannot-verify")
            codes = [r["code"] for r in result["reasons"]]
            self.assertIn("models-unestablished", codes)

    def test_product_model_not_in_fields_consumed_when_recipe_has_no_models(self):
        """Append product_model to fields_consumed ONLY after comparison has run."""
        recipe = copy.deepcopy(BASE_RECIPE)
        del recipe["target"]["models"]
        fp = {"product_device": "spacewar", "partition_scheme": "virtual_A/B", "bootloader_state": "unlocked"}
        result = verify(fp, recipe)
        consumed = result.get("evidence", {}).get("fields_consumed", [])
        self.assertNotIn("product_model", consumed)

    def test_supported_device_codes_alias_gives_definite_verdict_with_alias_named(self):
        recipe = dict(
            BASE_RECIPE,
            target={
                "product_device": "spacewar",
                "models": ["A063"],
                "partition_scheme": "virtual_A/B",
                "supported_device_codes": ["spacewar-eea", "spacewar-in"],
            },
        )
        fp = dict(fingerprint("unlocked", product_device="spacewar-eea", product_model="A063"))
        result = verify(fp, recipe)
        self.assertEqual(result["verdict"], "safe")
        self.assertTrue(
            any(
                reason.get("code") == "match-device-alias" and "spacewar-eea" in reason.get("message", "")
                for reason in result["reasons"]
            )
        )

    def test_definite_verdict_carries_record_id_timestamp_and_consumed_fields(self):
        fp = {
            "record_id": "rec-001",
            "capture_timestamp": "2026-09-08",
            "product_device": "spacewar",
            "product_model": "A063",
            "partition_scheme": "virtual_A/B",
            "bootloader_state": "unlocked",
        }
        result = verify(fp, BASE_RECIPE)
        self.assertEqual(result["verdict"], "safe")
        self.assertIn("evidence", result)
        self.assertEqual(result["evidence"]["record_id"], "rec-001")
        self.assertEqual(result["evidence"]["capture_timestamp"], "2026-09-08")
        self.assertTrue(
            {"product_device", "product_model", "partition_scheme", "bootloader_state"}.issubset(
                set(result["evidence"]["fields_consumed"])
            )
        )

    def test_v01_asset_product_device_mismatch_returns_unsafe(self):
        """v0.1 asset identity mismatch against target.product_device returns unsafe."""
        recipe = {
            "schema_version": "0.1",
            "recipe_id": "oriole-system-only",
            "target": {
                "product_device": "oriole",
                "models": ["GD1YQ"],
                "partition_scheme": "A/B",
            },
            "assets": [
                {
                    "asset_id": "system",
                    "role": "system",
                    "product_device": "raven",
                }
            ],
            "operations": [
                {"kind": "write-image", "partition": "system", "asset_id": "system"}
            ],
        }
        fp = {
            "product_device": "oriole",
            "product_model": "GD1YQ",
            "partition_scheme": "A/B",
        }
        result = verify(fp, recipe)
        self.assertEqual(result["verdict"], "unsafe")
        codes = [r["code"] for r in result["reasons"]]
        self.assertIn("asset-product_device-mismatch", codes)


class OperationVocabularyTest(unittest.TestCase):
    """Prove operation kinds, required unlocks and vocabulary constraints."""

    def test_reproduction_recipes_abstain_on_unlock_undeclared_for_operation(self):
        with open(ROOT / "data" / "recipes-v0.2" / "spacewar.json", encoding="utf-8") as fh:
            base = json.load(fh)
        fp = {"product_device": "Spacewar", "product_model": "A063", "partition_scheme": "virtual_A/B", "android_version": "15"}

        # 1. Unlock renamed, no marker
        r1 = copy.deepcopy(base)
        p = r1["prerequisites"].pop("bootloader_state")
        p.pop("unlock_class", None)
        p.pop("unlock_step", None)
        p["declared_by"] = "fastboot_flashing"
        r1["prerequisites"]["oem_status"] = p
        res1 = verify(dict(fp, oem_status="unlocked"), r1)
        self.assertEqual(res1["verdict"], "cannot-verify")
        codes1 = [r["code"] for r in res1["reasons"]]
        self.assertIn("unlock-undeclared-for-operation", codes1)

        # 2. write-image, no unlock prerequisite
        r2 = copy.deepcopy(base)
        r2["prerequisites"] = {
            "android_version": {
                "state": "OPEN",
                "required": 12,
                "compare": "exact_major",
                "declared_by": "requirements.android",
            }
        }
        r2["operations"] = [{"kind": "write-image", "partition": "boot"}]
        res2 = verify(dict(fp, android_version=12), r2)
        self.assertEqual(res2["verdict"], "cannot-verify")
        codes2 = [r["code"] for r in res2["reasons"]]
        self.assertIn("unlock-undeclared-for-operation", codes2)

    def test_write_image_with_only_android_version_prerequisite_abstains(self):
        recipe = copy.deepcopy(BASE_RECIPE)
        recipe["prerequisites"] = {
            "android_version": {
                "state": "OPEN",
                "required": 12,
                "compare": "exact_major",
                "declared_by": "requirements.android",
            }
        }
        recipe["operations"] = [{"kind": "write-image", "partition": "system"}]
        res = verify(dict(fingerprint("unlocked"), android_version=12), recipe)
        self.assertEqual(res["verdict"], "cannot-verify")
        codes = [r["code"] for r in res["reasons"]]
        self.assertIn("unlock-undeclared-for-operation", codes)

    def test_unrecognized_operation_kind_abstains(self):
        recipe = copy.deepcopy(BASE_RECIPE)
        recipe["operations"] = [{"kind": "flash-everything", "partition": "all"}]
        res = verify(fingerprint("unlocked"), recipe)
        self.assertEqual(res["verdict"], "cannot-verify")
        codes = [r["code"] for r in res["reasons"]]
        self.assertIn("operation-kind-unrecognized", codes)

    def test_empty_operations_list_abstains(self):
        recipe = copy.deepcopy(BASE_RECIPE)
        recipe["operations"] = []
        res = verify(fingerprint("unlocked"), recipe)
        self.assertEqual(res["verdict"], "cannot-verify")
        codes = [r["code"] for r in res["reasons"]]
        self.assertIn("operations-none-declared", codes)

    def test_schema_table_and_vocabulary_agree(self):
        vocab = CHECK_RECIPES.get_vocabulary()
        CHECK_RECIPES.check_schema_table_agrees_with_vocabulary(vocab)


class RefusedPrerequisiteNameTest(unittest.TestCase):
    """Refused prerequisite names fail recipe check and return cannot-verify in verify()."""

    def test_refused_prerequisite_name_fails_check_and_abstains_in_verify(self):
        recipe_path = ROOT / "data" / "recipes-v0.2" / "spacewar.json"
        with open(recipe_path, encoding="utf-8") as fh:
            recipe = json.load(fh)

        bad_recipe = copy.deepcopy(recipe)
        val = bad_recipe["prerequisites"].pop("bootloader_state")
        bad_recipe["prerequisites"]["bootloader_unlocked"] = val

        derive_fields = CHECK_RECIPES.get_derive_fields()
        vocab = CHECK_RECIPES.get_vocabulary()

        with self.assertRaises(AssertionError) as ctx:
            CHECK_RECIPES.check_recipe(bad_recipe, "bad_spacewar.json", derive_fields, vocab)
        err = str(ctx.exception)
        self.assertIn("bad_spacewar.json", err)
        self.assertIn("bootloader_unlocked", err)
        self.assertIn("bootloader_state", err)

        fp = {
            "product_device": "Spacewar",
            "product_model": "A063",
            "partition_scheme": "virtual_A/B",
            "bootloader_unlocked": "unlocked",
            "android_version": "15",
        }
        result = verify(fp, bad_recipe)
        self.assertEqual(result["verdict"], "cannot-verify")
        codes = [r["code"] for r in result["reasons"]]
        self.assertIn("prerequisite-name-refused", codes)


class VersionComparisonTest(unittest.TestCase):
    """Prove declared version comparisons: exact_major, minimum, equal, undeclared, and unparseable."""

    def _version_recipe(self, required, compare=None):
        recipe = copy.deepcopy(BASE_RECIPE)
        prereq = {
            "state": "OPEN",
            "required": required,
            "declared_by": "requirements.android",
            "source_evidence": "synthetic version test",
        }
        if compare is not None:
            prereq["compare"] = compare
        recipe["prerequisites"]["android_version"] = prereq
        return recipe

    def test_exact_major_comparison(self):
        recipe = self._version_recipe(12, compare="exact_major")
        for confirmed_val in ("12", 12, "12.1", "12.0.1"):
            fp = dict(fingerprint("unlocked"), android_version=confirmed_val)
            res = verify(fp, recipe)
            self.assertEqual(res["verdict"], "safe", f"exact_major failed on {confirmed_val}")
            codes = [r["code"] for r in res["reasons"]]
            self.assertIn("prerequisite-android_version-confirmed", codes)

        for mismatch_val in (13, "13", 11, "11", "13.0"):
            fp = dict(fingerprint("unlocked"), android_version=mismatch_val)
            res = verify(fp, recipe)
            self.assertEqual(res["verdict"], "unsafe", f"exact_major should fail mismatch on {mismatch_val}")
            codes = [r["code"] for r in res["reasons"]]
            self.assertIn("prerequisite-android_version-mismatch", codes)

    def test_minimum_comparison(self):
        recipe = self._version_recipe(12, compare="minimum")
        fp_pass = dict(fingerprint("unlocked"), android_version=13)
        res_pass = verify(fp_pass, recipe)
        self.assertEqual(res_pass["verdict"], "safe")
        self.assertIn("prerequisite-android_version-confirmed", [r["code"] for r in res_pass["reasons"]])

        fp_fail = dict(fingerprint("unlocked"), android_version=11)
        res_fail = verify(fp_fail, recipe)
        self.assertEqual(res_fail["verdict"], "unsafe")
        self.assertIn("prerequisite-android_version-below-minimum", [r["code"] for r in res_fail["reasons"]])

    def test_numeric_version_without_compare_abstains_comparison_undeclared(self):
        recipe = self._version_recipe(12)  # no compare
        fp = dict(fingerprint("unlocked"), android_version=12)
        res = verify(fp, recipe)
        self.assertEqual(res["verdict"], "cannot-verify")
        codes = [r["code"] for r in res["reasons"]]
        self.assertIn("prerequisite-android_version-comparison-undeclared", codes)

    def test_unparseable_observed_version_abstains(self):
        recipe = self._version_recipe(12, compare="exact_major")
        fp = dict(fingerprint("unlocked"), android_version="twelve")
        res = verify(fp, recipe)
        self.assertEqual(res["verdict"], "cannot-verify")
        codes = [r["code"] for r in res["reasons"]]
        self.assertIn("prerequisite-android_version-unparseable", codes)

    def test_categorical_unlocked_with_no_compare_confirms_under_default_equal(self):
        recipe = copy.deepcopy(BASE_RECIPE)
        # bootloader_state is categorical "unlocked" with no compare
        fp = fingerprint("unlocked")
        res = verify(fp, recipe)
        self.assertEqual(res["verdict"], "safe")
        codes = [r["code"] for r in res["reasons"]]
        self.assertIn("prerequisite-bootloader_state-confirmed", codes)


class SpacewarRealCaptureTest(unittest.TestCase):
    """Spacewar real matrix capture and synthetic variants."""

    def _load_real_spacewar_fingerprint(self):
        matrix_path = ROOT / "data" / "device-matrix.jsonl"
        with open(matrix_path, encoding="utf-8") as f:
            records = [json.loads(line) for line in f if line.strip()]
        for r in records:
            android = (r.get("detected") or {}).get("android") or {}
            if (android.get("product_device") or "").lower() == "spacewar":
                return dict(android)
        raise AssertionError("Real spacewar record not found in device-matrix.jsonl")

    def _load_spacewar_recipe(self):
        path = ROOT / "data" / "recipes-v0.2" / "spacewar.json"
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    def test_real_capture_is_unsafe_on_bootloader_state_mismatch(self):
        fp = self._load_real_spacewar_fingerprint()
        recipe = self._load_spacewar_recipe()
        res = verify(fp, recipe)
        self.assertEqual(res["verdict"], "unsafe")
        codes = [r["code"] for r in res["reasons"]]
        self.assertIn("prerequisite-bootloader_state-mismatch", codes)

    def test_synthetic_unlocked_spacewar_is_safe(self):
        # Synthetic test fixture: derived from the real record with bootloader_state set
        # to "unlocked". No real unlocked capture exists because unlocking wipes the device (Tier C).
        fp = self._load_real_spacewar_fingerprint()
        fp["bootloader_state"] = "unlocked"
        recipe = self._load_spacewar_recipe()
        res = verify(fp, recipe)
        self.assertEqual(res["verdict"], "safe")

    def test_synthetic_unlocked_spacewar_wrong_android_version_is_unsafe(self):
        fp = self._load_real_spacewar_fingerprint()
        fp["bootloader_state"] = "unlocked"
        fp["android_version"] = "14"
        recipe = self._load_spacewar_recipe()
        res = verify(fp, recipe)
        self.assertEqual(res["verdict"], "unsafe")
        codes = [r["code"] for r in res["reasons"]]
        self.assertIn("prerequisite-android_version-mismatch", codes)

    def test_synthetic_unlocked_spacewar_missing_android_version_abstains(self):
        fp = self._load_real_spacewar_fingerprint()
        fp["bootloader_state"] = "unlocked"
        del fp["android_version"]
        recipe = self._load_spacewar_recipe()
        res = verify(fp, recipe)
        self.assertEqual(res["verdict"], "cannot-verify")
        codes = [r["code"] for r in res["reasons"]]
        self.assertIn("missing-android_version", codes)


class UnlockGateDefectsTest(unittest.TestCase):
    """Prove fixes for unlock gate defects."""

    def test_renamed_unlock_prerequisite_omitted_unlock_class_abstains(self):
        """Rename unlock prerequisite to oem_unlocking_enabled, omit unlock_class, assert cannot-verify."""
        recipe = copy.deepcopy(BASE_RECIPE)
        recipe["prerequisites"] = {
            "oem_unlocking_enabled": {
                "state": "OPEN",
                "required": "unlocked",
                "source_evidence": "synthetic setting",
            }
        }
        fp = {
            "product_device": "spacewar",
            "product_model": "A063",
            "partition_scheme": "virtual_A/B",
            "oem_unlocking_enabled": "unlocked",
        }
        result = verify(fp, recipe)
        self.assertEqual(result["verdict"], "cannot-verify")
        codes = [r["code"] for r in result["reasons"]]
        self.assertIn("unlock-undeclared-for-operation", codes)

    def test_untested_zero_does_not_reach_safe(self):
        """Assert source.upstream_untested = 0 or 0.0 does not reach safe."""
        for zero_val in (0, 0.0):
            recipe = copy.deepcopy(BASE_RECIPE)
            recipe["source"]["upstream_untested"] = zero_val
            fp = fingerprint("unlocked")
            result = verify(fp, recipe)
            self.assertNotEqual(result["verdict"], "safe")
            self.assertEqual(result["verdict"], "cannot-verify")
            codes = [r["code"] for r in result["reasons"]]
            self.assertIn("recipe-untested-unrecognized", codes)


class StateIsNotRead(unittest.TestCase):
    """`state` is carried on every prerequisite and must never reach a verdict."""

    def _mutate_state(self, recipe, value):
        out = copy.deepcopy(recipe)
        for name, pre in (out.get("prerequisites") or {}).items():
            if isinstance(pre, dict) and "state" in pre:
                pre["state"] = value
        return out

    def test_state_value_cannot_change_a_verdict(self):
        """Same recipe, four different `state` values, one identical answer each time."""
        for recipe_name, recipe in (("locked-bootloader", BASE_RECIPE),):
            for fp_state in ("locked", "unlocked"):
                fp = fingerprint(fp_state)
                fp["record_id"] = "state-invariance"
                fp["capture_timestamp"] = "2026-09-13T00:00:00Z"
                baseline = verify(fp, recipe)
                for planted in ("CLOSED", "SATISFIED", "", None):
                    other = verify(fp, self._mutate_state(recipe, planted))
                    self.assertEqual(
                        other["verdict"], baseline["verdict"],
                        "%s/%s: setting state=%r changed the verdict." % (recipe_name, fp_state, planted))
                    self.assertEqual(
                        [r["code"] for r in other["reasons"]],
                        [r["code"] for r in baseline["reasons"]],
                        "%s/%s: setting state=%r changed the reasons." % (recipe_name, fp_state, planted))

    def test_state_is_never_named_in_the_evidence(self):
        """fields_consumed is what an auditor reads. It must not claim `state` was used."""
        fp = fingerprint("unlocked")
        fp["record_id"] = "state-evidence"
        fp["capture_timestamp"] = "2026-09-13T00:00:00Z"
        consumed = verify(fp, BASE_RECIPE).get("evidence", {}).get("fields_consumed") or []
        named = [f for f in consumed if "state" in str(f).split(".")]
        self.assertEqual(named, [], "fields_consumed names `state` (%r)." % (named,))


class UnlockOutOfBandTest(unittest.TestCase):
    """Prerequisites that cannot be established from device state (out-of-band unlock)."""

    def _oob_recipe(self, method="fastboot_fairphone", unlock_class="out_of_band"):
        recipe = copy.deepcopy(BASE_RECIPE)
        recipe["prerequisites"] = {
            "bootloader_state": {
                "state": "OPEN",
                "required": "unlocked",
                "unlock_class": unlock_class,
                "unlock_method": method,
                "unlock_step": True,
                "declared_by": "unlock_bootloader",
                "source_evidence": "synthetic oob unlock",
            }
        }
        return recipe

    def test_out_of_band_unlock_abstains_with_unlock_out_of_band_and_no_fingerprint(self):
        recipe = self._oob_recipe("fastboot_fairphone")
        for fp in (None, {}, fingerprint()):
            result = verify(fp, recipe)
            self.assertEqual(result["verdict"], "cannot-verify")
            codes = [r["code"] for r in result["reasons"]]
            self.assertIn("unlock-out-of-band", codes)
            oob_reasons = [r for r in result["reasons"] if r["code"] == "unlock-out-of-band"]
            self.assertTrue(all(r["result"] == "abstain" for r in oob_reasons))
            self.assertIn("guidance", result["evidence"])
            self.assertTrue(len(result["evidence"]["guidance"]["steps"]) > 0)

    def test_command_unlock_never_returns_unlock_out_of_band(self):
        recipe = self._oob_recipe("fastboot_nexus", unlock_class="command")
        for fp in (None, {}, fingerprint(), fingerprint("unlocked"), fingerprint("locked")):
            result = verify(fp, recipe)
            codes = [r["code"] for r in result["reasons"]]
            self.assertNotIn("unlock-out-of-band", codes,
                             "command unlock must never return unlock-out-of-band")
        safe_result = verify(fingerprint("unlocked"), recipe)
        self.assertEqual(safe_result["verdict"], "safe")

    def test_omitted_unlock_class_returns_unlock_undeclared_for_operation(self):
        recipe = copy.deepcopy(BASE_RECIPE)
        del recipe["prerequisites"]["bootloader_state"]["unlock_class"]
        result = verify(fingerprint("unlocked"), recipe)
        self.assertEqual(result["verdict"], "cannot-verify")
        codes = [r["code"] for r in result["reasons"]]
        self.assertIn("unlock-undeclared-for-operation", codes)
        self.assertNotIn("unlock-out-of-band", codes)

    def test_guidance_for_known_method_present_and_for_unknown_absent(self):
        known_recipe = self._oob_recipe("fastboot_sony")
        known_result = verify(None, known_recipe)
        self.assertIn("guidance", known_result["evidence"])
        self.assertIn("steps", known_result["evidence"]["guidance"])
        self.assertIn("link", known_result["evidence"]["guidance"])

        unknown_recipe = self._oob_recipe("fastboot_obscure_unknown_vendor")
        unknown_result = verify(None, unknown_recipe)
        self.assertNotIn("guidance", unknown_result["evidence"])


class UpstreamUntestedGateTest(unittest.TestCase):
    """A recipe derived from an upstream config marked untested must never reach safe."""

    def test_untested_recipe_cannot_reach_safe_even_with_confirmed_prerequisites(self):
        recipe = copy.deepcopy(BASE_RECIPE)
        recipe["source"]["upstream_untested"] = True

        fp = fingerprint("unlocked")
        result = verify(fp, recipe)
        self.assertNotEqual(result["verdict"], "safe")
        self.assertEqual(result["verdict"], "cannot-verify")
        codes = [r["code"] for r in result["reasons"]]
        self.assertIn("recipe-untested-upstream", codes)

        untested_reasons = [r for r in result["reasons"] if r["code"] == "recipe-untested-upstream"]
        self.assertEqual(len(untested_reasons), 1)
        self.assertEqual(untested_reasons[0]["result"], "abstain")
        self.assertIn("source.upstream_untested", untested_reasons[0]["fields"])

    def test_untested_string_value_also_triggers_gate(self):
        recipe = copy.deepcopy(BASE_RECIPE)
        recipe["source"]["upstream_untested"] = "untested"
        result = verify(fingerprint("unlocked"), recipe)
        self.assertEqual(result["verdict"], "cannot-verify")
        self.assertIn("recipe-untested-upstream", [r["code"] for r in result["reasons"]])

    def test_legacy_source_untested_field_abstains_with_legacy_field_reason(self):
        """A recipe carrying source.untested abstains with recipe-untested-legacy-field."""
        recipe = copy.deepcopy(BASE_RECIPE)
        del recipe["source"]["upstream_untested"]
        recipe["source"]["untested"] = True
        result = verify(fingerprint("unlocked"), recipe)
        self.assertEqual(result["verdict"], "cannot-verify")
        codes = [r["code"] for r in result["reasons"]]
        self.assertIn("recipe-untested-legacy-field", codes)

    def test_unrecognized_upstream_untested_value_abstains_with_recipe_defect_reason(self):
        for bad_val in ("marked", "yes", "True", 123):
            recipe = copy.deepcopy(BASE_RECIPE)
            recipe["source"]["upstream_untested"] = bad_val
            result = verify(fingerprint("unlocked"), recipe)
            self.assertEqual(result["verdict"], "cannot-verify")
            codes = [r["code"] for r in result["reasons"]]
            self.assertIn("recipe-untested-unrecognized", codes)

    def test_not_untested_recipe_returns_byte_identical_reasons(self):
        baseline_recipe = copy.deepcopy(BASE_RECIPE)
        baseline_result = verify(fingerprint("unlocked"), baseline_recipe)
        self.assertEqual(baseline_result["verdict"], "safe")

        tested_recipe = copy.deepcopy(BASE_RECIPE)
        tested_recipe["source"]["upstream_untested"] = False
        result = verify(fingerprint("unlocked"), tested_recipe)
        self.assertEqual(result["verdict"], "safe")
        self.assertEqual(
            result["reasons"], baseline_result["reasons"],
            "reasons must be byte-identical when recipe is not marked untested",
        )

    def test_absent_upstream_untested_returns_byte_identical_reasons(self):
        baseline_recipe = copy.deepcopy(BASE_RECIPE)
        baseline_result = verify(fingerprint("unlocked"), baseline_recipe)

        for unestablished_val in ("unestablished", None):
            recipe = copy.deepcopy(BASE_RECIPE)
            recipe["source"]["upstream_untested"] = unestablished_val
            result = verify(fingerprint("unlocked"), recipe)
            self.assertEqual(result["verdict"], baseline_result["verdict"])
            self.assertEqual(
                result["reasons"], baseline_result["reasons"],
                "reasons must be byte-identical when upstream untested field is absent/unestablished",
            )

    def test_untested_recipe_with_hardware_mismatch_is_still_unsafe(self):
        recipe = copy.deepcopy(BASE_RECIPE)
        recipe["source"]["upstream_untested"] = True

        result = verify(fingerprint("locked"), recipe)
        self.assertEqual(result["verdict"], "unsafe")
        self.assertIn("prerequisite-bootloader_state-mismatch", [r["code"] for r in result["reasons"]])

    def test_upstream_untested_field_never_named_in_fields_consumed(self):
        recipe = copy.deepcopy(BASE_RECIPE)
        recipe["source"]["upstream_untested"] = True

        fp = fingerprint("unlocked")
        fp["record_id"] = "untested-evidence-test"
        result = verify(fp, recipe)
        consumed = result.get("evidence", {}).get("fields_consumed", [])
        for f in consumed:
            self.assertNotIn("source", str(f))
            self.assertNotIn("upstream_untested", str(f))


if __name__ == "__main__":
    unittest.main()
