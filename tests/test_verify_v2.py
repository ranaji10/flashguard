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


class UnlockGateDefectsTest(unittest.TestCase):
    """Prove fixes for unlock gate defects 5a and 6."""

    def test_renamed_unlock_prerequisite_omitted_unlock_class_abstains(self):
        """Rename unlock prerequisite to oem_unlocking_enabled, omit unlock_class, assert cannot-verify."""
        recipe = copy.deepcopy(BASE_RECIPE)
        recipe["prerequisites"] = {
            "oem_unlocking_enabled": {
                "state": "OPEN",
                "required": "unlocked",
                "unlock_step": True,
                "declared_by": "unlock_bootloader",
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
        self.assertIn("unlock-class-undeclared", codes)

    def test_unlock_operation_without_marked_unlock_prerequisite_abstains(self):
        """Declare unlock_bootloader operation with no marked unlock prerequisite, assert cannot-verify."""
        recipe = copy.deepcopy(BASE_RECIPE)
        recipe["operations"] = [{"kind": "unlock_bootloader", "partition": "bootloader"}]
        recipe["prerequisites"] = {
            "android_version": {
                "state": "OPEN",
                "required": 12,
                "declared_by": "requirements.android",
                "source_evidence": "synthetic requirement",
            }
        }
        fp = {
            "product_device": "spacewar",
            "product_model": "A063",
            "partition_scheme": "virtual_A/B",
            "android_version": 12,
        }
        result = verify(fp, recipe)
        self.assertEqual(result["verdict"], "cannot-verify")
        codes = [r["code"] for r in result["reasons"]]
        self.assertIn("unmarked-unlock-step", codes)

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

    def test_declared_by_unlock_treated_as_unlock_step_without_operations_entry(self):
        """Assert a prerequisite whose declared_by names an unlock is treated as unlock step without operations entry."""
        recipe = copy.deepcopy(BASE_RECIPE)
        recipe["operations"] = []
        recipe["prerequisites"] = {
            "custom_unlock": {
                "state": "OPEN",
                "required": "unlocked",
                "declared_by": "unlock_bootloader",
                "source_evidence": "source config unlock step",
            }
        }
        fp = {
            "product_device": "spacewar",
            "product_model": "A063",
            "partition_scheme": "virtual_A/B",
            "custom_unlock": "unlocked",
        }
        result = verify(fp, recipe)
        self.assertEqual(result["verdict"], "cannot-verify")
        codes = [r["code"] for r in result["reasons"]]
        self.assertIn("unlock-class-undeclared", codes)


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


def _get_capture_fields_and_mapping():
    derive_sh = ROOT / "bench-kit" / "scripts" / "derive.sh"
    with open(derive_sh, encoding="utf-8") as f:
        derive_content = f.read()
    derive_fields = set(re.findall(r"^p\s+([a-zA-Z0-9_]+)", derive_content, re.MULTILINE))

    schema_md = ROOT / "data" / "schema.md"
    with open(schema_md, encoding="utf-8") as f:
        schema_content = f.read()

    schema_android_fields = set()
    android_match = re.search(r'"android":\s*\{([^}]+)\}', schema_content)
    if android_match:
        schema_android_fields = set(re.findall(r'"([a-zA-Z0-9_]+)":', android_match.group(1)))

    mapping = {}
    in_mapping_table = False
    for line in schema_content.splitlines():
        if "## Prerequisite condition to fingerprint evidence mapping" in line:
            in_mapping_table = True
            continue
        if in_mapping_table:
            if line.startswith("## "):
                break
            match = re.search(r"\|\s*`?([a-zA-Z0-9_]+)`?\s*\|\s*`?([a-zA-Z0-9_]+)`?\s*\|", line)
            if match:
                k, v = match.groups()
                if k not in ("Prerequisite condition", "---", "Value", "Field"):
                    mapping[k] = v

    capture_fields = derive_fields | schema_android_fields
    return capture_fields, mapping


def check_recipe_prerequisites_produceable(recipe, recipe_name="<recipe>"):
    capture_fields, mapping = _get_capture_fields_and_mapping()
    prerequisites = recipe.get("prerequisites") or {}
    for prereq_name in prerequisites.keys():
        evidence_field = mapping.get(prereq_name, prereq_name)
        if evidence_field not in capture_fields:
            raise AssertionError(
                f"Recipe '{recipe_name}' prerequisite '{prereq_name}' requires evidence field "
                f"'{evidence_field}' which is produced by no capture route."
            )


class RecipePrerequisitesProduceableTest(unittest.TestCase):
    """Fail the build when a recipe names a prerequisite whose evidence field appears in no capture route."""

    def test_all_recipes_on_disk_require_only_producible_fields(self):
        for recipe_dir in (ROOT / "data" / "recipes", ROOT / "data" / "recipes-v0.2"):
            if not recipe_dir.is_dir():
                continue
            for recipe_path in sorted(recipe_dir.glob("*.json")):
                with open(recipe_path, encoding="utf-8") as fh:
                    recipe = json.load(fh)
                check_recipe_prerequisites_produceable(recipe, recipe_path.name)

    def test_unproduced_prerequisite_field_fails_check_with_informative_error(self):
        bad_recipe = copy.deepcopy(BASE_RECIPE)
        bad_recipe["prerequisites"] = {
            "unproduced_hardware_sensor": {
                "state": "OPEN",
                "required": "active",
            }
        }
        with self.assertRaises(AssertionError) as ctx:
            check_recipe_prerequisites_produceable(bad_recipe, "bad_recipe.json")
        msg = str(ctx.exception)
        self.assertIn("bad_recipe.json", msg)
        self.assertIn("unproduced_hardware_sensor", msg)
        self.assertIn("no capture route", msg)


if __name__ == "__main__":
    unittest.main()
