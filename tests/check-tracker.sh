#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
#
# The tracker is the one document nothing checked.
#
# check-index.sh looks for dangling paths, but only ones written in `backticks`, and the
# tracker writes them as plain prose. So the file naming the most paths in the project was
# the file the path check silently skipped, and three references to the pre-split docs/
# layout survived there for a week: docs/bench-run-2026-08-29.md, docs/participation-note.md
# and docs/testing-protocol.md, none of which have existed since 6 September.
#
# Same shape as the publication scan that exempted the only file that could fail it. A check
# that looks like it covers something and does not is worse than no check, because it also
# supplies the confidence.
#
# The tracker is gitignored on purpose -- it carries names that must not reach a public
# repository -- so a clone will not have it. Absent is fine and says so. Present and wrong
# is build-failing.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"; ROOT="$(cd "$HERE/.." && pwd)"
TRACKER="$ROOT/docs/tracker/open-items.html"

if [ ! -f "$TRACKER" ]; then
  echo "  no tracker on this machine (gitignored by design) -- nothing to check"
  exit 0
fi

python3 - "$TRACKER" "$ROOT" <<'PY'
import json, os, re, sys

tracker, root = sys.argv[1], sys.argv[2]
src = open(tracker, encoding="utf-8").read()
m = re.search(r'<script id="appdata" type="application/json">(.*?)</script>', src, re.S)
if not m:
    print("  TRACKER: no appdata block. The page will render blank in a browser too.")
    sys.exit(1)
try:
    d = json.loads(m.group(1))
except json.JSONDecodeError as e:
    print("  TRACKER: appdata is not valid JSON (%s)." % e)
    print("      The page renders blank in a browser. Fix it there and the page comes back.")
    sys.exit(1)

fail = 0
items = [(s["id"], i) for s in d["sections"] for i in s["items"]]

# ---- 1. every path the tracker names must exist ----------------------------
PATH = re.compile(
    r'\b((?:docs|tests|data|grant|bench-kit|flashguard|\.github|\.githooks|\.vscode)'
    # longest extension first, or 'jsonl' matches as 'js' and the path is truncated
    r'/[A-Za-z0-9_./-]*\.(?:jsonl|json|html|yaml|md|sh|py|js))(?![A-Za-z0-9])')
missing = {}
for sec, it in items:
    for field in ("t", "d", "note"):
        for p in PATH.findall(str(it.get(field, ""))):
            if not os.path.exists(os.path.join(root, p)):
                missing.setdefault(p, set()).add(it["id"])
if missing:
    print("  TRACKER NAMES FILES THAT DO NOT EXIST:")
    for p in sorted(missing):
        print("      %-46s in %s" % (p, ", ".join(sorted(missing[p]))))
    print("      An item pointing at a path that moved is an item nobody can act on.")
    fail = 1

# ---- 1b. the Caveman list has to be followable ------------------------------
# It exists to be acted on without thinking, by someone with ten minutes. Every path it
# names has to open and every item it points at has to exist, or the first dead link
# teaches you to stop trusting the other seven. A chip that renders an apology is worse
# than a chip that is not there.
cave = d.get("caveman") or []
ids = {i["id"] for _, i in items}
if not cave:
    print("  THE CAVEMAN LIST IS EMPTY.")
    print("      The page has a Caveman chip, so an empty list is a button that opens")
    print("      an apology. Either write the next steps or take the chip out.")
    fail = 1
else:
    bad = []
    for ix, c in enumerate(cave, 1):
        for w in c.get("where") or []:
            if not os.path.exists(os.path.join(root, w)):
                bad.append(("dead path", ix, w))
        # An item is REQUIRED now, not optional. The step reads its number, its status
        # and its countdown off that item; with no item there is nothing to read and the
        # step can never mark itself done, which is the whole point of the rebuild.
        if not c.get("item"):
            bad.append(("no item", ix, "(step belongs to nothing)"))
        elif c["item"] not in ids:
            bad.append(("unknown item", ix, c["item"]))
        for k in ("act", "why", "rec"):
            if not str(c.get(k) or "").strip():
                bad.append(("blank " + k, ix, "(empty)"))
    if bad:
        print("  THE CAVEMAN LIST POINTS AT THINGS THAT ARE NOT THERE:")
        for kind, num, val in bad:
            print("      step %-3s %-14s %s" % (num, kind, val))
        print("      This list is meant to be followed without checking. It has to resolve.")
        fail = 1

# ---- 2. the currency stamp must not contradict the data --------------------
stamp = d.get("stamp") or {}
touched = sorted({i.get("touched") for _, i in items if i.get("touched")})
newest = touched[-1] if touched else None
if newest and stamp.get("swept") and newest > stamp["swept"]:
    print("  STAMP IS BEHIND THE DATA:")
    print("      the banner says swept %s, but items were moved as late as %s"
          % (stamp["swept"], newest))
    print("      The banner exists to answer \"is this current?\" without reading anything.")
    print("      A sync that moved items should either update the sweep line or not claim one.")
    fail = 1

# ---- 3. the moved filter must not be empty ---------------------------------
# It is the only way to see what changed, and it fails silently: an empty filter looks
# exactly like a sweep that changed nothing.
import datetime
if newest:
    since = (datetime.date.fromisoformat(newest) - datetime.timedelta(days=7)).isoformat()
    visible = [i["id"] for _, i in items
               if i.get("touched") and i["touched"] >= since]
    if not visible:
        print("  THE \"MOVED RECENTLY\" FILTER SHOWS NOTHING.")
        print("      No item was touched in the seven days to %s, so the filter that exists"
              % newest)
        print("      to show what changed is empty, and empty looks exactly like unchanged.")
        fail = 1
else:
    since = None

if not fail:
    n = len(items)
    recent = len([i for _, i in items
                  if since and i.get("touched") and i["touched"] >= since])
    stamp2 = d.get("stamp") or {}
    upd = d.get("updated") or ""
    for _, i in items:
        if i.get("touched") and i["touched"] > upd:
            upd = i["touched"]
    fp = "%s|%s|%s" % (upd, stamp2.get("swept") or "", stamp2.get("commit") or "")
    for _, i in items:
        fp += "|%s:%s:%s:%s:%s" % (i["id"], i["status"], i.get("touched") or "",
                                   i.get("d") or "", i.get("note") or "")
    for ix, c in enumerate(cave):
        fp += "|cave%d:%s:%s:%s:%s:%s" % (
            ix, c.get("act") or "", c.get("why") or "",
            c.get("rec") or "", ",".join(c.get("where") or []), c.get("item") or "")
    h = 5381
    _u = fp.encode("utf-16-le")
    for _k in range(0, len(_u), 2):
        h = ((h * 33) ^ int.from_bytes(_u[_k:_k + 2], "little")) & 0xFFFFFFFF
    print("  %d tracker items, %d moved in the seven days to %s; %d caveman steps;"
          " version %08x" % (n, recent, newest or "?", len(cave), h))
    print("      every path named exists. The page prints this version in its banner --"
          " if it shows another, that copy is behind.")
sys.exit(fail)
PY
