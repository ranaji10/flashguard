import glob
import json
import os
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RECIPE_DIR = os.path.join(ROOT, "data", "recipes")


class VerdictGapTest(unittest.TestCase):
    def test_recipes_record_both_assessments_and_explain_agreement(self):
        paths = sorted(glob.glob(os.path.join(RECIPE_DIR, "*.json")))
        self.assertEqual(len(paths), 5)

        for path in paths:
            with open(path, encoding="utf-8") as handle:
                recipe = json.load(handle)

            self.assertIn("human_assessment", recipe, path)
            self.assertIn("expected_verdict", recipe, path)
            self.assertIn(recipe["human_assessment"], {"safe", "unsafe", "cannot-verify"}, path)
            self.assertIn(recipe["expected_verdict"], {"safe", "unsafe", "cannot-verify"}, path)
            if recipe["human_assessment"] != recipe["expected_verdict"]:
                self.assertTrue(recipe.get("verdict_gap_reason"), path)


if __name__ == "__main__":
    unittest.main()
