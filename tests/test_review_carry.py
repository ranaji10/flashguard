# SPDX-License-Identifier: GPL-3.0-or-later
"""review_carry_list.py counts a finding once and flags one filed against an older file."""
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOL = ROOT / "tests" / "review_carry_list.py"
FIRST = subprocess.run(["git", "rev-list", "--max-parents=0", "HEAD"], cwd=ROOT,
                       capture_output=True, text=True).stdout.split()[0]


class ReviewCarry(unittest.TestCase):
    def run_tool(self, text, *args):
        with tempfile.TemporaryDirectory() as tmp:
            log = pathlib.Path(tmp, "log.md")
            log.write_text(text)
            return subprocess.run([sys.executable, str(TOOL), str(log), *args],
                                  capture_output=True, text=True).stdout

    def test_duplicate_in_one_review_counts_once_and_fenced_copies_are_ignored(self):
        text = ("## 2026-09-20 — %s — x\n\n- [ ] README.md:1 same finding\n- [ ] README.md:1 same finding\n"
                "```\n- [ ] README.md:1 same finding\n```\n" % FIRST[:7])
        self.assertEqual(self.run_tool(text, "--count").strip(), "1")

    def test_file_changed_since_filed_is_flagged_not_closed(self):
        text = "## 2026-09-20 — uncommitted-on-%s — x\n\n- [ ] README.md:1 a finding\n" % FIRST[:7]
        out = self.run_tool(text)
        self.assertIn("FILED AGAINST AN OLDER VERSION of README.md", out)
        self.assertIn("- [ ] README.md:1 a finding", out)

    def test_ticked_findings_are_not_carried(self):
        self.assertEqual(self.run_tool("## 2026-09-20 — abc1234 — x\n\n- [x] a.py:1 done\n", "--count").strip(), "0")


if __name__ == "__main__":
    unittest.main()
