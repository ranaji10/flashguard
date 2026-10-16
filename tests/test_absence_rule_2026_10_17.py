# SPDX-License-Identifier: GPL-3.0-or-later
"""The layout absence rule of 17 October 2026, each part held by a test that fails without it.

See docs/reasoning/layout-absence-rule.md.

No Android property ever says "this phone has one set of partitions". A/B phones say so
positively, through three independent markers. The rule: on stock firmware (user build,
release-keys) running Android 8 or later, when all three markers were queried and all three
are empty, the verifier reads the layout as single. Anywhere outside that scope it abstains
exactly as before.
"""
import copy
import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from flashguard import verify  # noqa: E402

ABSENT = "no ab_update, no slot_suffix, no virtual_ab -- absent is not the same as single"

# The real Galaxy A52s captured on 13 Oct 2026 (kit 2026-10-08), allowlisted fields only.
A52S = {
    "product_model": "SM-A528B", "product_device": "a52sxq", "manufacturer": "samsung",
    "board_platform": "taro", "chipset_family": "QTI SM7325", "android_version": "14", "sdk": "34",
    "build_fingerprint": "samsung/a52sxqxx/a52sxq:14/UP1A.231005.007/A528BXXSDFXK1:user/release-keys",
    "partition_scheme": "unknown", "partition_basis": ABSENT, "slot_suffix": "unknown",
    "bootloader_state": "locked", "bootloader_basis": "ro.boot.flash.locked=1",
    "verified_boot_state": "green", "firmware_origin": "stock", "build_type": "user",
    "build_tags": "release-keys", "first_api_level": "30", "dynamic_partitions": "true",
    "treble_enabled": "true",
}

RECIPE = json.loads((ROOT / "data" / "recipes-v0.2" / "a52sxq.json").read_text())


def run(**changes):
    fp = dict(A52S)
    for k, v in changes.items():
        if v is None:
            fp.pop(k, None)
        else:
            fp[k] = v
    return verify(fp, copy.deepcopy(RECIPE))


def layout_reason(result):
    hits = [r for r in result["reasons"] if "partition" in r["code"]]
    assert len(hits) == 1, hits
    return hits[0]


class AbsenceRule(unittest.TestCase):
    def test_stock_android_8_plus_with_no_marker_reads_as_single(self):
        res = run()
        r = layout_reason(res)
        self.assertEqual(r["code"], "match-partition_scheme-inferred-single")
        self.assertEqual(r["result"], "pass")
        # Right recipe, bootloader locked: the A52s's own recipe file predicted this.
        self.assertEqual(res["verdict"], "not-ready")

    def test_inferred_single_against_an_ab_recipe_is_a_mismatch(self):
        recipe = copy.deepcopy(RECIPE)
        recipe["target"]["partition_scheme"] = "A/B"
        res = verify(dict(A52S), recipe)
        r = layout_reason(res)
        self.assertEqual(r["code"], "partition-scheme-mismatch-inferred")
        self.assertEqual(res["verdict"], "unsafe")

    def test_below_android_8_abstains(self):
        self.assertEqual(layout_reason(run(sdk="25", android_version="7.1.2"))["code"], "missing-partition_scheme")

    def test_custom_firmware_abstains(self):
        self.assertEqual(layout_reason(run(firmware_origin="custom"))["code"], "missing-partition_scheme")

    def test_userdebug_build_abstains_even_with_a_stock_fingerprint(self):
        # The J3 and the Xperia mini pro run custom builds that keep the stock fingerprint.
        self.assertEqual(layout_reason(run(build_type="userdebug"))["code"], "missing-partition_scheme")

    def test_test_keys_abstain(self):
        self.assertEqual(layout_reason(run(build_tags="test-keys"))["code"], "missing-partition_scheme")

    def test_markers_not_queried_abstains(self):
        # "unknown" basis means the properties were never read, not that they were empty.
        self.assertEqual(layout_reason(run(partition_basis="unknown"))["code"], "missing-partition_scheme")

    def test_any_slot_suffix_blocks_the_inference(self):
        self.assertEqual(layout_reason(run(slot_suffix="_a"))["code"], "missing-partition_scheme")

    def test_older_capture_without_build_fields_uses_the_fingerprint(self):
        res = run(build_type=None, build_tags=None)
        self.assertEqual(layout_reason(res)["code"], "match-partition_scheme-inferred-single")

    def test_older_capture_with_a_non_release_fingerprint_abstains(self):
        res = run(build_type=None, build_tags=None,
                  build_fingerprint="samsung/a52sxqxx/a52sxq:14/UP1A/X:userdebug/test-keys")
        self.assertEqual(layout_reason(res)["code"], "missing-partition_scheme")

    def test_unknown_firmware_origin_abstains(self):
        self.assertEqual(layout_reason(run(firmware_origin="unknown"))["code"], "missing-partition_scheme")

    def test_a_reported_layout_is_never_overridden(self):
        r = layout_reason(run(partition_scheme="A/B", partition_basis="ro.build.ab_update=true"))
        self.assertEqual(r["code"], "partition-scheme-mismatch")

    def test_the_inference_is_named_in_the_evidence(self):
        res = run()
        for field in ("partition_basis", "firmware_origin", "sdk"):
            self.assertIn(field, res["evidence"]["fields_consumed"])


if __name__ == "__main__":
    unittest.main()
