# SPDX-License-Identifier: GPL-3.0-or-later
"""The five rulings of 8 October 2026, each held by a test that fails without it.

See docs/reasoning/rulings-2026-10-08.md.
  1. The model is settled from credible public sources; the person holding the phone is
     asked only when those cannot settle it, and is shown the links (revised the same day:
     capture itself asks nothing).
  2. Custom firmware is in scope: identity a ROM wrote can confirm, never condemn, and a
     stock-firmware prerequisite cannot be read from a phone not running stock firmware.
  3. Tier A is reported per storage layout.
  4. merge.py never reconciles two phones whose chipsets differ.
  5. postmarketOS is one of the upstream sources checked for captured phones.
"""
import copy
import io
import json
import pathlib
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "data"))

from flashguard import verify  # noqa: E402

LINEAGE_SPACEWAR = {"project": "LineageOS", "url": "https://wiki.lineageos.org/devices/Spacewar/",
                    "consulted": "2026-10-08", "models": ["A063"]}

RECIPE = {
    "schema_version": "0.3",
    "recipe_id": "rulings-fixture",
    "source": {"device_facts_from": "synthetic", "consulted": "2026-10-08",
               "authored": "independent", "upstream_untested": "unestablished"},
    "target": {"product_device": "Spacewar", "models": ["A063"], "models_sources": [LINEAGE_SPACEWAR],
               "partition_scheme": "virtual_A/B"},
    "install_method": "fastboot_nexus",
    "prerequisites": {
        "bootloader_state": {"state": "OPEN", "required": "unlocked", "unlock_class": "command",
                             "unlock_step": True, "declared_by": "unlock_bootloader",
                             "source_evidence": "synthetic"},
        "android_version": {"state": "OPEN", "required": "15", "compare": "exact_major",
                            "declared_by": "before_install.version", "source_evidence": "synthetic"},
    },
    "operations": [{"kind": "write-image", "partition": "vendor_boot"}],
    "source_fields_unused": [],
}

FP = {"product_device": "Spacewar", "product_model": "A063", "partition_scheme": "virtual_A/B",
      "bootloader_state": "unlocked", "android_version": "15", "firmware_origin": "stock"}

# The OnePlus 6T case: every upstream source for fajita names the codename, none lists a model,
# and two LineageOS entries share the codename with different install methods.
FAJITA_THIS = {"project": "LineageOS", "url": "https://wiki.lineageos.org/devices/fajita/",
               "consulted": "2026-10-08", "models": []}
FAJITA_OAI = {"project": "OpenAndroidInstaller", "consulted": "2026-10-08", "models": [],
              "url": "https://github.com/openandroidinstaller-dev/openandroidinstaller/blob/main/openandroidinstaller/assets/configs/fajita.yaml"}
FAJITA_TMO = {"project": "LineageOS", "url": "https://wiki.lineageos.org/devices/fajita/variant2/",
              "consulted": "2026-10-08", "models": [], "name": "6T (T-Mobile)"}


def fajita_recipe(**target):
    r = copy.deepcopy(RECIPE)
    r["target"] = {"product_device": "fajita", "supported_device_codes": ["fajita", "OnePlus6T"],
                   "partition_scheme": "A/B", "models_sources": [FAJITA_THIS, FAJITA_OAI],
                   "competing_sources": [FAJITA_TMO]}
    r["target"].update(target)
    r["prerequisites"]["android_version"]["required"] = "11"
    return r


SIXT = {"product_device": "OnePlus6T", "product_model": "ONEPLUS A6013", "partition_scheme": "A/B",
        "bootloader_state": "unlocked", "android_version": "11", "firmware_origin": "stock"}


def run(fp=None, recipe=None, **changes):
    f = copy.deepcopy(FP if fp is None else fp)
    f.update(changes)
    return verify(f, copy.deepcopy(RECIPE if recipe is None else recipe))


def codes(result, kind=None):
    return [r["code"] for r in result["reasons"] if kind is None or r["result"] == kind]


class ModelFromSourcesRuling(unittest.TestCase):
    """Revised 8 Oct: capture asks the tester nothing. The verifier settles the model from
    credible sources, and asks the person only when those sources cannot settle it."""

    def test_model_listed_by_a_credible_source_decides_without_asking_anyone(self):
        res = run()
        self.assertEqual(res["verdict"], "safe")
        self.assertNotIn("confirmation_request", res["evidence"])

    def test_model_absent_from_every_credible_list_is_unsafe_on_stock(self):
        res = run(product_model="A065")
        self.assertEqual(res["verdict"], "unsafe")
        self.assertIn("model-mismatch", codes(res, "fail"))

    def test_a_list_with_no_credible_source_cannot_decide(self):
        for src in ({"url": "data/recipes/notes.md", "models": ["A063"]},
                    {"url": "https://example.invalid/a063", "models": ["A063"]},
                    {"url": "https://wiki.lineageos.org.evil.example/x", "models": ["A063"]},
                    {"models": ["A063"]}):
            recipe = copy.deepcopy(RECIPE)
            recipe["target"]["models_sources"] = [src]
            res = run(recipe=recipe)
            self.assertEqual(res["verdict"], "not-ready", src)  # pending the person's confirmation
            self.assertTrue(res.get("pending_confirmation"), src)
            self.assertIn("model-needs-confirmation", codes(res, "abstain"), src)

    def test_a_recipe_model_no_credible_source_lists_is_not_used(self):
        recipe = copy.deepcopy(RECIPE)
        recipe["target"]["models"] = ["A063", "A065"]
        self.assertEqual(run(recipe=recipe, product_model="A065")["verdict"], "unsafe")

    def test_6t_sources_cannot_decide_so_the_result_asks_with_every_link(self):
        res = verify(SIXT, fajita_recipe())
        self.assertEqual(res["verdict"], "not-ready")  # pending confirmation (evening ruling)
        self.assertIn("model-needs-confirmation", codes(res, "abstain"))
        req = res["evidence"]["confirmation_request"]
        self.assertIn("ONEPLUS A6013", req["observed_models"])
        self.assertEqual({s["url"] for s in req["recipe_sources"]}, {FAJITA_THIS["url"], FAJITA_OAI["url"]})
        self.assertEqual([s["url"] for s in req["cannot_tell_apart_from"]], [FAJITA_TMO["url"]])
        self.assertTrue(req["question"])

    def test_a_credible_model_list_settles_the_6t_without_asking(self):
        # Settled only when nothing competing is left unexcluded: without the T-Mobile page.
        gsm = {"project": "public", "url": "https://www.gsmarena.com/oneplus_6t-9350.php",
               "consulted": "2026-10-08", "models": ["ONEPLUS A6010", "ONEPLUS A6013"]}
        res = verify(SIXT, fajita_recipe(models_sources=[FAJITA_THIS, FAJITA_OAI, gsm], competing_sources=[]))
        self.assertEqual(res["verdict"], "safe")
        self.assertNotIn("confirmation_request", res["evidence"])

    def test_the_persons_answer_settles_it_only_for_this_recipes_source(self):
        ok = dict(SIXT, model_confirmation="human_confirmed", model_confirmed_source=FAJITA_THIS["url"])
        self.assertEqual(verify(ok, fajita_recipe())["verdict"], "safe")
        other = dict(SIXT, model_confirmation="human_confirmed", model_confirmed_source=FAJITA_TMO["url"])
        res = verify(other, fajita_recipe())
        self.assertEqual(res["verdict"], "cannot-verify")
        self.assertIn("model-confirmed-elsewhere", codes(res, "abstain"))
        no_source = dict(SIXT, model_confirmation="human_confirmed")
        self.assertEqual(verify(no_source, fajita_recipe())["verdict"], "cannot-verify")

    def test_a_person_saying_no_is_never_a_pass(self):
        res = verify(dict(SIXT, model_confirmation="human_rejected"), fajita_recipe())
        self.assertEqual(res["verdict"], "cannot-verify")
        self.assertIn("model-rejected-by-person", codes(res, "abstain"))

    def test_an_answer_cannot_override_a_credible_list(self):
        fp = dict(FP, product_model="A065", model_confirmation="human_confirmed",
                  model_confirmed_source=LINEAGE_SPACEWAR["url"])
        self.assertEqual(verify(fp, copy.deepcopy(RECIPE))["verdict"], "unsafe")

    def test_hardware_sku_can_carry_the_listed_model(self):
        res = run(product_model="motorola edge 30 ultra", hardware_sku="A063")
        self.assertEqual(res["verdict"], "safe")

    def test_locked_6t_is_not_ready_only_once_the_model_is_settled(self):
        locked = dict(SIXT, bootloader_state="locked")
        pending = verify(locked, fajita_recipe())
        self.assertEqual(pending["verdict"], "not-ready")
        self.assertTrue(pending.get("pending_confirmation"))
        settled = dict(locked, model_confirmation="human_confirmed", model_confirmed_source=FAJITA_THIS["url"])
        self.assertEqual(verify(settled, fajita_recipe())["verdict"], "not-ready")


class CustomFirmwareRuling(unittest.TestCase):
    def test_rom_written_identity_mismatch_abstains_instead_of_unsafe(self):
        res = run(firmware_origin="custom", product_device="halium_arm64", product_model="Generic Device",
                  android_version="9")
        self.assertEqual(res["verdict"], "cannot-verify")
        self.assertIn("identity-custom-firmware", codes(res, "abstain"))
        self.assertEqual(codes(res, "fail"), [])

    def test_vendor_or_lineage_device_can_confirm_on_custom_firmware(self):
        res = run(firmware_origin="custom", product_device="halium_arm64", vendor_device="Spacewar",
                  product_model="Generic Device", vendor_model="A063")
        self.assertIn("match-device-custom-firmware", codes(res, "pass"))

    def test_stock_version_prerequisite_cannot_be_read_on_custom_firmware(self):
        res = run(firmware_origin="custom")
        self.assertEqual(res["verdict"], "cannot-verify")
        self.assertIn("firmware-version-custom-rom", codes(res, "abstain"))
        self.assertNotIn("prerequisite-android_version-confirmed", codes(res))

    def test_custom_firmware_never_reaches_safe_through_a_rom_model_string(self):
        # product_model is written by the ROM; with no vendor model or SKU there is nothing to match.
        res = run(firmware_origin="custom", android_version="15")
        self.assertNotEqual(res["verdict"], "safe")

    def test_stock_identity_mismatch_is_still_unsafe(self):
        res = run(product_device="a5xelte", product_model="SM-A510F")
        self.assertEqual(res["verdict"], "unsafe")

    def test_unknown_origin_behaves_as_before(self):
        res = run(firmware_origin="unknown")
        self.assertEqual(res["verdict"], "safe")


class TierAPerLayout(unittest.TestCase):
    def test_gate_reports_each_layout_separately(self):
        import coverage
        a = {"manufacturer": "x", "product_model": "m", "chipset_family": "c", "android_version": "15",
             "bootloader_state": "locked", "verified_boot_state": "green"}
        ab = dict(a, partition_scheme="virtual_A/B", product_device="ab1", build_fingerprint="f1")
        nab = dict(a, partition_scheme="unknown", product_device="nab1", build_fingerprint="f2",
                   chipset_family="d")
        recs = [{"detected": {"device_class": "adb", "android": ab}},
                {"detected": {"device_class": "adb", "android": nab}}]
        out = io.StringIO()
        with redirect_stdout(out):
            coverage.tier_a_gate(recs, recs, [])
        text = out.getvalue()
        self.assertIn("A/B or virtual A/B, all seven fields", text)
        self.assertIn("layout not reported, the other six fields", text)
        self.assertRegex(text, r"A/B or virtual A/B, all seven fields\s+1")
        self.assertRegex(text, r"layout not reported, the other six fields\s+1")
        self.assertRegex(text, r"distinct phones complete for their layout\s+2 of 10")


class MergeNeverJoinsDifferentChipsets(unittest.TestCase):
    def test_halium_phones_on_different_chips_stay_two_devices(self):
        import merge
        key = merge.reconcile_key if hasattr(merge, "reconcile_key") else None
        self.assertIsNotNone(key, "merge.reconcile_key is the single place the join key is made")
        base = {"reported_device": "x", "detected": {"android": {"manufacturer": "halium",
                "product_model": "Generic Device", "product_device": "halium_arm64"}}}
        mi = copy.deepcopy(base); mi["detected"]["android"]["board_platform"] = "sdm660"
        redmi = copy.deepcopy(base); redmi["detected"]["android"]["board_platform"] = "mt6768"
        self.assertNotEqual(key(mi), key(redmi))


class PostmarketOSIsChecked(unittest.TestCase):
    def test_pmaports_codename_is_found(self):
        import coverage
        with tempfile.TemporaryDirectory() as tmp:
            d = pathlib.Path(tmp) / "pmaports" / "device" / "testing" / "device-samsung-j3xnlte"
            d.mkdir(parents=True)
            (d / "deviceinfo").write_text('deviceinfo_name="Samsung Galaxy J3"\ndeviceinfo_codename="samsung-j3xnlte"\n')
            where = coverage.upstream_sources_for({"product_device": "j3xnlte", "product_model": "SM-J320FN"}, tmp)
            self.assertIn("postmarketOS", where)

    def test_alias_and_model_lists_are_read(self):
        import coverage
        with tempfile.TemporaryDirectory() as tmp:
            lw = pathlib.Path(tmp) / "lineage_wiki" / "_data" / "devices"
            lw.mkdir(parents=True)
            (lw / "larry_variant1.yml").write_text("codename: larry\nmodels: [CPH2467, CPH2465]\n")
            oai = pathlib.Path(tmp) / "openandroidinstaller" / "openandroidinstaller" / "assets" / "configs"
            oai.mkdir(parents=True)
            (oai / "fajita.yaml").write_text("metadata:\n  device_code: fajita\n  supported_device_codes:\n    - fajita\n    - OnePlus6T\n")
            self.assertIn("LineageOS", coverage.upstream_sources_for({"product_device": "OP5958L1", "product_model": "CPH2467"}, tmp))
            self.assertIn("OpenAndroidInstaller", coverage.upstream_sources_for({"product_device": "OnePlus6T", "product_model": "ONEPLUS A6013"}, tmp))


class CountingOnceKeepsTheConfirmedRead(unittest.TestCase):
    def test_identical_reads_are_represented_by_the_decided_one(self):
        import coverage
        obs = ("Spacewar", "A063")
        runs = [{"observation": obs, "verdict": "cannot-verify"},
                {"observation": obs, "verdict": "not-ready"},
                {"observation": obs, "verdict": "cannot-verify"}]
        out = coverage.distinct(runs)
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["verdict"], "not-ready")


class ConfirmModelTool(unittest.TestCase):
    def test_writes_one_line_and_refuses_a_second(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("confirm_model", ROOT / "tools" / "confirm-model.py")
        mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
        with tempfile.TemporaryDirectory() as tmp:
            m = pathlib.Path(tmp) / "m.jsonl"; o = pathlib.Path(tmp) / "c.jsonl"
            m.write_text(json.dumps({"record_id": "r1", "tester": "T", "device_local_id": "p",
                                     "detected": {"android": {"product_model": "A063"}}}) + "\n")
            with redirect_stdout(io.StringIO()):
                mod.main(["--record-id", "r1", "--source", "https://wiki.lineageos.org/devices/Spacewar/", "--by", "T",
                          "--matrix", str(m), "--out", str(o)])
            line = json.loads(o.read_text().strip())
            self.assertEqual(line["model_confirmation"], "human_confirmed")
            self.assertEqual(line["model_confirmed_source"], "https://wiki.lineageos.org/devices/Spacewar/")
            with self.assertRaises(SystemExit):
                mod.main(["--record-id", "r1", "--source", "https://wiki.lineageos.org/devices/Spacewar/", "--by", "T",
                          "--matrix", str(m), "--out", str(o)])


class ConfusionIsResolvedThroughSources(unittest.TestCase):
    """When codename and model disagree, the credible sources decide; failing that, ask."""

    LARRY = {"project": "LineageOS", "url": "https://wiki.lineageos.org/devices/larry/", "consulted": "2026-10-08",
             "models": ["CPH2467", "CPH2465"], "name": "OnePlus Nord CE 3 Lite 5G"}
    N30 = {"project": "LineageOS", "url": "https://wiki.lineageos.org/devices/larry/variant2/", "consulted": "2026-10-08",
           "models": ["CPH2513"], "name": "OnePlus Nord N30 5G"}
    EQS = {"project": "LineageOS", "url": "https://wiki.lineageos.org/devices/eqs/", "consulted": "2026-10-08",
           "models": ["XT2241-1", "XT2241-2"], "name": "Motorola edge 30 ultra"}

    def recipe(self, device, sources, competing=(), scheme="virtual_A/B"):
        r = copy.deepcopy(RECIPE)
        r["target"] = {"product_device": device, "partition_scheme": scheme,
                       "models_sources": list(sources), "competing_sources": list(competing)}
        r["prerequisites"]["android_version"]["required"] = "15"
        return r

    def test_stock_codename_differs_but_credible_model_code_matches(self):
        nord = {"product_device": "OP5958L1", "product_model": "CPH2467", "partition_scheme": "virtual_A/B",
                "bootloader_state": "locked", "android_version": "15", "firmware_origin": "stock"}
        res = verify(nord, self.recipe("larry", [self.LARRY], [self.N30]))
        self.assertEqual(res["verdict"], "not-ready")
        self.assertIn("match-device-by-model", codes(res, "pass"))

    def test_sibling_model_under_the_same_codename_is_still_unsafe(self):
        n30 = {"product_device": "larry", "product_model": "CPH2513", "partition_scheme": "virtual_A/B",
               "bootloader_state": "unlocked", "android_version": "15", "firmware_origin": "stock"}
        res = verify(n30, self.recipe("larry", [self.LARRY], [self.N30]))
        self.assertEqual(res["verdict"], "unsafe")
        self.assertIn("model-mismatch", codes(res, "fail"))

    def test_marketing_name_instead_of_code_is_asked_not_condemned(self):
        edge = {"product_device": "eqs", "product_model": "motorola edge 30 ultra", "manufacturer": "motorola",
                "partition_scheme": "virtual_A/B", "bootloader_state": "locked", "android_version": "15",
                "firmware_origin": "stock"}
        res = verify(edge, self.recipe("eqs", [self.EQS]))
        self.assertEqual(res["verdict"], "not-ready")
        self.assertTrue(res.get("pending_confirmation"))
        self.assertIn("model-needs-confirmation", codes(res, "abstain"))
        self.assertEqual(codes(res, "fail"), [])
        self.assertEqual(res["evidence"]["confirmation_request"]["recipe_sources"][0]["url"], self.EQS["url"])

    def test_the_sku_settles_the_marketing_name_case_without_asking(self):
        edge = {"product_device": "eqs", "product_model": "motorola edge 30 ultra", "hardware_sku": "XT2241-1",
                "partition_scheme": "virtual_A/B", "bootloader_state": "locked", "android_version": "15",
                "firmware_origin": "stock"}
        self.assertEqual(verify(edge, self.recipe("eqs", [self.EQS]))["verdict"], "not-ready")

    def test_a_genuinely_different_phone_is_still_unsafe(self):
        other = {"product_device": "a5xelte", "product_model": "SM-A510F", "partition_scheme": "virtual_A/B",
                 "bootloader_state": "unlocked", "android_version": "15", "firmware_origin": "stock"}
        res = verify(other, self.recipe("larry", [self.LARRY], [self.N30]))
        self.assertEqual(res["verdict"], "unsafe")


class CredibleSourcesAsWritten(unittest.TestCase):
    """GSMArena and makers' sites count (ruled 8 Oct). They write codes their own way."""

    GSM_6T = {"project": "GSMArena", "url": "https://www.gsmarena.com/oneplus_6t-9350.php",
              "consulted": "2026-10-08", "models": ["A6010", "A6013"], "name": "OnePlus 6T"}

    def test_manufacturer_prefix_and_case_do_not_hide_a_listed_code(self):
        fp = dict(SIXT, manufacturer="OnePlus")
        res = verify(fp, fajita_recipe(models_sources=[FAJITA_THIS, FAJITA_OAI, self.GSM_6T], competing_sources=[]))
        self.assertEqual(res["verdict"], "safe")

    def test_a_different_code_with_the_same_prefix_is_still_unsafe(self):
        fp = dict(SIXT, manufacturer="OnePlus", product_model="ONEPLUS A6003")
        res = verify(fp, fajita_recipe(models_sources=[FAJITA_THIS, FAJITA_OAI, self.GSM_6T]))
        self.assertEqual(res["verdict"], "unsafe")

    def test_only_the_manufacturers_own_name_is_stripped(self):
        fp = dict(SIXT, manufacturer="Xiaomi", product_model="ONEPLUS A6013")
        res = verify(fp, fajita_recipe(models_sources=[FAJITA_THIS, FAJITA_OAI, self.GSM_6T]))
        self.assertEqual(res["verdict"], "unsafe")

    def test_forums_on_a_makers_domain_are_not_credible(self):
        forum = {"url": "https://forum.fairphone.com/t/fairphone-model-identification/81036", "models": ["A063"]}
        recipe = copy.deepcopy(RECIPE)
        recipe["target"]["models_sources"] = [forum]
        self.assertIn("model-needs-confirmation", codes(run(recipe=recipe), "abstain"))

    def test_makers_support_site_is_credible(self):
        maker = {"url": "https://support.fairphone.com/hc/en-us/articles/x", "models": ["A063"]}
        recipe = copy.deepcopy(RECIPE)
        recipe["target"]["models_sources"] = [maker]
        self.assertEqual(run(recipe=recipe)["verdict"], "safe")


class PendingConfirmationIsNotReady(unittest.TestCase):
    """Ruled 8 Oct, evening: when sources cannot settle the model, the verdict is not-ready
    pending the person's confirmation, with where the sources disagree and the device
    configurations the verifier cannot choose between. Same logic in testing and in public."""

    def test_6t_with_nothing_else_missing_is_not_ready_pending_confirmation(self):
        res = verify(SIXT, fajita_recipe())
        self.assertEqual(res["verdict"], "not-ready")
        self.assertTrue(res.get("pending_confirmation"))
        req = res["evidence"]["confirmation_request"]
        self.assertTrue(req["mismatch"])
        configs = {c["url"] for c in req["possible_configs"]}
        self.assertIn(FAJITA_TMO["url"], configs)
        self.assertIn(FAJITA_THIS["url"], configs)

    def test_pending_is_never_safe_and_never_hides_an_unsafe(self):
        self.assertNotEqual(verify(SIXT, fajita_recipe())["verdict"], "safe")
        other = dict(SIXT, product_device="a5xelte", product_model="SM-A510F")
        self.assertEqual(verify(other, fajita_recipe())["verdict"], "unsafe")

    def test_any_other_abstention_keeps_cannot_verify_but_still_explains(self):
        res = verify(dict(SIXT, partition_scheme="unknown"), fajita_recipe())
        self.assertEqual(res["verdict"], "cannot-verify")
        self.assertIn("confirmation_request", res["evidence"])

    def test_a_listed_code_a_codeless_variant_cannot_exclude_is_pending(self):
        gsm = {"project": "GSMArena", "url": "https://www.gsmarena.com/oneplus_6t-9350.php",
               "consulted": "2026-10-08", "models": ["A6010", "A6013"], "name": "OnePlus 6T"}
        fp = dict(SIXT, manufacturer="OnePlus")
        res = verify(fp, fajita_recipe(models_sources=[FAJITA_THIS, FAJITA_OAI, gsm]))
        self.assertEqual(res["verdict"], "not-ready")
        self.assertTrue(res.get("pending_confirmation"))
        self.assertIn("model-ambiguous-variant", codes(res, "abstain"))
        mism = res["evidence"]["confirmation_request"]["mismatch"]
        self.assertTrue(any("6T (T-Mobile)" in str(m) for m in mism))

    def test_a_competing_variant_that_lists_other_codes_is_excluded(self):
        c = ConfusionIsResolvedThroughSources
        nord = {"product_device": "OP5958L1", "product_model": "CPH2467", "partition_scheme": "virtual_A/B",
                "bootloader_state": "unlocked", "android_version": "15", "firmware_origin": "stock"}
        res = verify(nord, c.recipe(c, "larry", [c.LARRY], [c.N30]))
        self.assertEqual(res["verdict"], "safe")
        self.assertFalse(res.get("pending_confirmation"))

    def test_the_persons_answer_turns_pending_into_a_decision(self):
        fp = dict(SIXT, model_confirmation="human_confirmed", model_confirmed_source=FAJITA_THIS["url"])
        res = verify(fp, fajita_recipe())
        self.assertEqual(res["verdict"], "safe")
        self.assertFalse(res.get("pending_confirmation"))

    def test_pending_runs_are_not_counted_as_decided(self):
        import coverage
        runs = [{"observation": ("a",), "verdict": "not-ready", "pending_confirmation": True, "paired": True},
                {"observation": ("b",), "verdict": "not-ready", "paired": True}]
        self.assertEqual(coverage.decided_count(runs), 1)


class SlotsAreSlots(unittest.TestCase):
    def test_a_recipe_for_ab_accepts_a_virtual_ab_phone(self):
        r = copy.deepcopy(RECIPE); r["target"]["partition_scheme"] = "A/B"
        self.assertEqual(verify(copy.deepcopy(FP), r)["verdict"], "safe")

    def test_a_recipe_for_virtual_ab_does_not_accept_plain_ab(self):
        self.assertEqual(run(partition_scheme="A/B")["verdict"], "unsafe")

    def test_single_never_matches_slots(self):
        r = copy.deepcopy(RECIPE); r["target"]["partition_scheme"] = "single"
        self.assertEqual(verify(copy.deepcopy(FP), r)["verdict"], "unsafe")


if __name__ == "__main__":
    unittest.main(verbosity=1)
