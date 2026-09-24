#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""List carried review findings, oldest first, with two protections added 24 September 2026.

1. A finding filed twice in one review (the filer used to re-file carried findings) is shown
   once. "Survived five reviews" was counting copies.
2. A finding whose cited file has changed since the commit it was filed against is marked
   FILED AGAINST AN OLDER VERSION. It is NOT closed automatically: a rewrite can carry a defect
   forward. It only stops a stale finding being presented as a fresh one.

Usage: python3 tests/review_carry_list.py [path/to/review-log.md]   (prints; exit 0)
       --count   prints only the number of distinct open findings
"""
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
LOG = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else ROOT / "docs/reference/review-log.md"


def parse(text):
    sections, fence, cur, finding = [], False, None, None
    for line in text.splitlines():
        if line.startswith("```"):
            fence = not fence
            continue
        if fence:
            continue
        if line.startswith("## "):
            cur = {"head": line, "open": []}
            sections.append(cur)
            finding = None
            continue
        if cur is None:
            continue
        if line.startswith("- [ ]"):
            finding = [line[5:].strip()]
            cur["open"].append(finding)
            continue
        if re.match(r"- \[[xX]\]", line):
            finding = None
            continue
        if finding is not None and re.match(r"^\s+\S", line):
            finding.append(line.strip())
            continue
        finding = None
    return sections


def commit_of(head):
    m = re.search(r"(?:uncommitted-on-)?\b([0-9a-f]{7,40})\b", head)
    return m.group(1) if m else None


def changed_since(sha, path):
    if not sha or not path:
        return None
    try:
        r = subprocess.run(["git", "diff", "--quiet", sha, "--", path], cwd=ROOT,
                           capture_output=True, text=True)
    except OSError:
        return None
    return {0: False, 1: True}.get(r.returncode)


def main():
    if not LOG.is_file():
        print("no review log")
        return 0
    sections = parse(LOG.read_text(encoding="utf-8"))
    total = 0
    blocks = []
    for age_from_newest, sec in enumerate(sections):
        seen, uniq = set(), []
        for f in sec["open"]:
            key = f[0][:120]
            if key in seen:
                continue
            seen.add(key)
            uniq.append(f)
        if not uniq:
            continue
        total += len(uniq)
        blocks.append((age_from_newest, sec["head"], uniq))
    if "--count" in sys.argv:
        print(total)
        return 0
    for later, head, uniq in reversed(blocks):
        age = "(newest review)" if later == 0 else "(carried through %d later review%s)" % (later, "" if later == 1 else "s")
        print()
        if later >= 2:
            print("  >>> SURVIVED %d REVIEWS. This is a decision now, not a finding." % later)
        print(head + "  " + age)
        sha = commit_of(head)
        for f in uniq:
            m = re.match(r"`?([\w./-]+\.\w+)(?::\d+)?`?", f[0])
            path = m.group(1) if m else None
            stale = changed_since(sha, path)
            if stale:
                print("  [FILED AGAINST AN OLDER VERSION of %s: re-verify or tick]" % path)
            print("  - [ ] " + "\n        ".join(f))
    print()
    print("%d distinct finding(s) carried." % total)
    return 0


if __name__ == "__main__":
    sys.exit(main())
