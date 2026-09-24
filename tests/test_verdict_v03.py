# SPDX-License-Identifier: GPL-3.0-or-later
"""not-ready, the verdict scope, plain reasons, recipe format v0.3, and counting a phone once.

Each test names the defect it guards against. Remove the fix and the test fails.
"""
import copy
import importlib.util
import json
import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from flashguard import verify
from flashguard.reasons import KINDS

SPEC = importlib.util.spec_from_file_location("coverage_module", ROOT / "data" / "coverage.py")
COVERAGE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(COVERAGE)

BASE = {
    "schema_version": "0.2",
    "recipe_id": "t",
    "source": {"device_facts_from": "synthetic", "consulted": "2026-09-24", "authored": "independent",
               "upstream_untested": "unestablished"},
    "target": {"product_device": "spacewar", "models": ["A063"], "partition_scheme": "virtual_A/B"},
    "install_method": "fastboot_nexus",
    "prerequisites": {"bootloader_state": {"required": "unlocked", "unlock_class": "command", "unlock_step": True,
                                           "declared_by": "unlock_bootloader", "source_evidence": "synthetic"}},
    "operations": [{"kind": "write-image", "partition": "system"}],
    "source_fields_unused": [],
}


def MATRIX():
    return (ROOT / "data" / "device-matrix.jsonl").read_text(encoding="utf-8").splitlines()


def fp(**kw):
    base = {"product_device": "spacewar", "product_model": "A063", "partition_scheme": "virtual_A/B"}
    base.update(kw)
    return base


def v03(prereqs):
    r = copy.deepcopy(BASE)
    r["schema_version"] = "0.3"
    r["prerequisites"] = prereqs
    return r


def codes(res):
    return [x["code"] for x in res["reasons"]]


class NotReady(unittest.TestCase):
    def test_locked_phone_right_recipe_is_not_ready_with_remedy(self):
        res = verify(fp(bootloader_state="locked"), BASE)
        self.assertEqual(res["verdict"], "not-ready")
        unmet = [x for x in res["reasons"] if x["result"] == "unmet"]
        self.assertEqual(len(unmet), 1)
        self.assertIn("Unlock", unmet[0]["remedy"])

    def test_identity_mismatch_wins_over_not_ready(self):
        res = verify(fp(bootloader_state="locked", product_model="A065"), BASE)
        self.assertEqual(res["verdict"], "unsafe")

    def test_not_ready_needs_confirmed_identity(self):
        """A phone that did not report its layout may not fit the recipe, so it cannot be 'not ready'."""
        res = verify(fp(bootloader_state="locked", partition_scheme="unknown"), BASE)
        self.assertEqual(res["verdict"], "cannot-verify")
        self.assertIn("prerequisite-bootloader_state-mismatch", codes(res))

    def test_not_ready_is_never_counted_as_a_false_safe_or_as_safe(self):
        res = verify(fp(bootloader_state="locked"), BASE)
        self.assertNotEqual(res["verdict"], "safe")
        COVERAGE.enforce_false_safe_gate([{"expected": "unsafe", "human_assessment": "unsafe", "verdict": res["verdict"]}])

    def test_version_mismatch_remedy_names_both_versions(self):
        r = copy.deepcopy(BASE)
        r["prerequisites"]["android_version"] = {"required": "15", "compare": "exact_major", "source_evidence": "s"}
        res = verify(fp(bootloader_state="unlocked", android_version="16"), r)
        self.assertEqual(res["verdict"], "not-ready")
        remedy = [x for x in res["reasons"] if x["result"] == "unmet"][0]["remedy"]
        self.assertIn("16", remedy)
        self.assertIn("15", remedy)


class ScopeAndPlainReasons(unittest.TestCase):
    CASES = [
        (fp(bootloader_state="unlocked"), BASE),
        (fp(bootloader_state="locked"), BASE),
        (fp(), BASE),
        (fp(product_device="other"), BASE),
        ({}, {"schema_version": "9"}),
        (fp(), {"schema_version": "0.1", "recipe_id": "x", "target": {"product_device": "spacewar",
                "partition_scheme": "virtual_A/B", "models": ["A063"]}, "assets": [], "operations": []}),
    ]

    def test_every_verdict_carries_scope(self):
        for f, r in self.CASES:
            res = verify(f, r)
            self.assertIn("scope", res)
            self.assertTrue(res["scope"]["not_checked"], "scope must say what was not checked")

    def test_every_reason_has_a_known_kind_and_plain_text(self):
        for f, r in self.CASES:
            for reason in verify(f, r)["reasons"]:
                self.assertIn(reason["kind"], KINDS, reason["code"])
                self.assertTrue(reason["plain"])

    def test_every_corpus_reason_is_classified(self):
        records = [json.loads(l) for l in MATRIX() if l.strip()]
        for d in ("recipes", "recipes-v0.2"):
            for run in COVERAGE.corpus_runs(str(ROOT / "data" / d), records):
                for code, _res, kind, _p in run["reasons"]:
                    self.assertNotEqual(kind, "unclassified", code)

    def test_verify_is_pure(self):
        f, r = fp(bootloader_state="locked"), copy.deepcopy(BASE)
        f0, r0 = copy.deepcopy(f), copy.deepcopy(r)
        a, b = verify(f, r), verify(f, r)
        self.assertEqual(a, b)
        self.assertEqual(f, f0)
        self.assertEqual(r, r0)


class FormatV03(unittest.TestCase):
    def readback(self):
        return {"bootloader_state": {"required": "unlocked", "unlock_class": "out_of_band", "unlock_step": True,
                                     "unlock_readback": "device", "declared_by": "d", "source_evidence": "s"}}

    def test_readback_locked_is_not_ready(self):
        self.assertEqual(verify(fp(bootloader_state="locked"), v03(self.readback()))["verdict"], "not-ready")

    def test_readback_unlocked_is_safe(self):
        self.assertEqual(verify(fp(bootloader_state="unlocked"), v03(self.readback()))["verdict"], "safe")

    def test_out_of_band_without_readback_still_abstains(self):
        p = self.readback(); del p["bootloader_state"]["unlock_readback"]
        res = verify(fp(bootloader_state="unlocked"), v03(p))
        self.assertEqual(res["verdict"], "cannot-verify")
        self.assertIn("unlock-out-of-band", codes(res))

    def test_unknown_readback_value_abstains(self):
        p = self.readback(); p["bootloader_state"]["unlock_readback"] = "user_says_so"
        res = verify(fp(bootloader_state="unlocked"), v03(p))
        self.assertEqual(res["verdict"], "cannot-verify")
        self.assertIn("unlock-readback-unrecognized", codes(res))

    def test_v03_field_in_v02_recipe_is_invalid(self):
        r = v03(self.readback()); r["schema_version"] = "0.2"
        res = verify(fp(bootloader_state="unlocked"), r)
        self.assertIn("invalid-recipe", codes(res))

    def test_one_of(self):
        p = self.readback()
        p["android_version"] = {"required": ["13", "14"], "compare": "one_of", "source_evidence": "s"}
        r = v03(p)
        self.assertEqual(verify(fp(bootloader_state="unlocked", android_version="13"), r)["verdict"], "safe")
        self.assertEqual(verify(fp(bootloader_state="unlocked", android_version="14.0"), r)["verdict"], "safe")
        self.assertEqual(verify(fp(bootloader_state="unlocked", android_version="15"), r)["verdict"], "not-ready")
        p["android_version"]["required"] = "14"
        res = verify(fp(bootloader_state="unlocked", android_version="14"), v03(p))
        self.assertEqual(res["verdict"], "cannot-verify")

    def test_no_step_never_reaches_safe(self):
        p = {"bootloader_state": {"requirement": "no_step", "source_evidence": "source declares none"}}
        res = verify(fp(bootloader_state="unlocked"), v03(p))
        self.assertEqual(res["verdict"], "cannot-verify")
        self.assertIn("unlock-no-step-declared", codes(res))
        self.assertNotIn("unlock-undeclared-for-operation", codes(res))

    def test_no_step_without_evidence_is_refused(self):
        res = verify(fp(), v03({"bootloader_state": {"requirement": "no_step"}}))
        self.assertIn("unlock-requirement-unrecognized", codes(res))


class RealRecipes(unittest.TestCase):
    def load(self, name):
        return json.loads((ROOT / "data" / "recipes-v0.2" / name).read_text())

    def test_real_a52s_capture_lists_locked_but_cannot_say_not_ready(self):
        rec = [json.loads(l) for l in MATRIX() if '"a52sxq"' in l][0]
        res = verify(rec["detected"]["android"], self.load("a52sxq.json"))
        self.assertEqual(res["verdict"], "cannot-verify")
        self.assertIn("missing-partition_scheme", codes(res))
        self.assertIn("prerequisite-bootloader_state-mismatch", codes(res))

    def test_a52s_that_reports_its_layout_is_not_ready_while_locked(self):
        rec = [json.loads(l) for l in MATRIX() if '"a52sxq"' in l][0]
        f = dict(rec["detected"]["android"], partition_scheme="single")
        self.assertEqual(verify(f, self.load("a52sxq.json"))["verdict"], "not-ready")

    def test_avicii_relabelled_safe_and_reaches_safe_only_when_unlocked_on_12(self):
        r = self.load("avicii.json")
        self.assertEqual(r["human_assessment"], "safe")
        self.assertTrue(r.get("verdict_gap_reason"))
        base = {"product_device": "avicii", "product_model": "AC2001", "partition_scheme": "A/B"}
        self.assertEqual(verify(dict(base, bootloader_state="unlocked", android_version="12"), r)["verdict"], "safe")
        self.assertEqual(verify(dict(base, bootloader_state="locked", android_version="12"), r)["verdict"], "not-ready")
        self.assertEqual(verify(dict(base, bootloader_state="unlocked", android_version="13"), r)["verdict"], "not-ready")


class CountingOnce(unittest.TestCase):
    def test_same_phone_read_three_times_counts_once(self):
        rec = [json.loads(l) for l in MATRIX() if '"Spacewar"' in l]
        self.assertGreaterEqual(len(rec), 3)
        runs = COVERAGE.corpus_runs(str(ROOT / "data" / "recipes-v0.2"), rec)
        spacewar = [r for r in runs if r["recipe_id"].startswith("spacewar") and r["paired"]]
        self.assertGreaterEqual(len(spacewar), 3)
        self.assertEqual(len(COVERAGE.distinct(spacewar)), 1)

    def test_a_changed_phone_counts_again(self):
        rec = [json.loads(l) for l in MATRIX() if '"Spacewar"' in l][0]
        changed = copy.deepcopy(rec)
        changed["detected"]["android"]["security_patch"] = "2026-09-01"
        runs = COVERAGE.corpus_runs(str(ROOT / "data" / "recipes-v0.2"), [rec, changed])
        spacewar = [r for r in runs if r["recipe_id"].startswith("spacewar")]
        self.assertEqual(len(COVERAGE.distinct(spacewar)), 2)

    def test_gate_share_uses_distinct_phones(self):
        runs = [{"paired": True, "verdict": "not-ready", "observation": ("a", 1)}] * 3 + \
               [{"paired": True, "verdict": "cannot-verify", "observation": ("b", 1)}]
        COVERAGE.enforce_verifier_gate(runs, floor_data={"decided_over_paired": 0.5})
        with self.assertRaises(SystemExit):
            COVERAGE.enforce_verifier_gate(runs, floor_data={"decided_over_paired": 0.6})


class AbstentionKinds(unittest.TestCase):
    def test_honest_and_our_gap_are_told_apart(self):
        honest = {"reasons": [("missing-partition_scheme", "abstain", "honest", "")]}
        gap = {"reasons": [("missing-partition_scheme", "abstain", "honest", ""),
                           ("prerequisites-none-declared", "abstain", "our_gap", "")]}
        self.assertEqual(COVERAGE.abstention_kind(honest), "honest")
        self.assertEqual(COVERAGE.abstention_kind(gap), "our_gap")


class UnpairedDevices(unittest.TestCase):
    def test_phone_without_recipe_is_listed_with_upstream_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            lineage = pathlib.Path(tmp, "lineage_wiki", "_data", "devices")
            lineage.mkdir(parents=True)
            (lineage / "sunfish.yml").write_text("codename: sunfish\n")
            rec = {"detected": {"device_class": "adb", "android": {"product_device": "sunfish", "product_model": "Pixel 4a"}}}
            rec2 = {"detected": {"device_class": "adb", "android": {"product_device": "nowhere", "product_model": "X"}}}
            out = COVERAGE.report_unpaired_devices([rec, rec2], COVERAGE.load_all_recipes(), upstream=tmp)
        notes = dict((d, n) for d, _m, n in out)
        self.assertIn("LineageOS", notes["sunfish"])
        self.assertIn("no upstream recipe", notes["nowhere"])


if __name__ == "__main__":
    unittest.main()
