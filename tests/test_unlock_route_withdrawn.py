# SPDX-License-Identifier: GPL-3.0-or-later
"""Unlock route withdrawn by the maker, 17 October 2026.

Some makers stopped offering any official way to unlock the bootloader (Huawei stopped issuing
unlock codes; LineageOS says of the P smart that no official method is available). For such a
phone, "not-ready, unlock it first" sends the person after something that does not exist.

A recipe states this on its unlock prerequisite: "unlock_route": "withdrawn_by_maker". Then:
  - a phone that reports locked gets cannot-verify, reason unlock-route-withdrawn (honest);
  - a phone that reports unlocked (unlocked earlier, or by an unofficial route) is checked as
    usual, because what the phone reports is what matters;
  - any other value is our gap, never a pass.
See docs/reasoning/recipe-format.md.
"""
import copy
import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from flashguard import verify  # noqa: E402

FIGO = json.loads((ROOT / "data" / "recipes-v0.2" / "figo.json").read_text())
MATRIX = [json.loads(l) for l in (ROOT / "data" / "device-matrix.jsonl").read_text().splitlines() if l.strip()]
P_SMART = [r["detected"]["android"] for r in MATRIX
           if (r.get("detected") or {}).get("android", {}).get("product_model") == "FIG-LX1"][0]


def codes(res):
    return [r["code"] for r in res["reasons"]]


class UnlockRouteWithdrawn(unittest.TestCase):
    def test_figo_declares_the_route_withdrawn(self):
        self.assertEqual(FIGO["prerequisites"]["bootloader_state"].get("unlock_route"), "withdrawn_by_maker")

    def test_locked_phone_with_withdrawn_route_is_cannot_verify_not_not_ready(self):
        res = verify(dict(P_SMART), copy.deepcopy(FIGO))
        self.assertEqual(res["verdict"], "cannot-verify")
        self.assertIn("unlock-route-withdrawn", codes(res))
        self.assertNotIn("prerequisite-bootloader_state-mismatch", codes(res))

    def test_phone_already_unlocked_is_checked_as_usual(self):
        res = verify(dict(P_SMART, bootloader_state="unlocked", bootloader_basis="ro.boot.flash.locked=0"),
                     copy.deepcopy(FIGO))
        self.assertNotIn("unlock-route-withdrawn", codes(res))
        self.assertIn("prerequisite-bootloader_state-confirmed", codes(res))

    def test_unrecognised_route_value_never_passes(self):
        recipe = copy.deepcopy(FIGO)
        recipe["prerequisites"]["bootloader_state"]["unlock_route"] = "maybe"
        res = verify(dict(P_SMART, bootloader_state="unlocked"), recipe)
        self.assertIn("unlock-route-unrecognized", codes(res))
        self.assertNotEqual(res["verdict"], "safe")

    def test_available_is_the_same_as_absent(self):
        recipe = copy.deepcopy(FIGO)
        recipe["prerequisites"]["bootloader_state"]["unlock_route"] = "available"
        self.assertEqual(verify(dict(P_SMART), recipe)["verdict"], "not-ready")

    def test_route_is_a_v03_field(self):
        recipe = copy.deepcopy(FIGO)
        recipe["schema_version"] = "0.2"
        res = verify(dict(P_SMART), recipe)
        self.assertIn("invalid-recipe", codes(res))


if __name__ == "__main__":
    unittest.main()
