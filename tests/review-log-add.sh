#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
#
# File a review into docs/reference/review-log.md.
#
#     pbpaste | bash tests/review-log-add.sh "short label"
#
# WHY THIS EXISTS. The first time a review came back, filing it meant reading five
# paragraphs of prose and hand-writing checkboxes from them. That works once. Done every
# time, it is the step that gets skipped, and then the log stops being written while the
# ritual still appears to run -- the same failure the three-review rule guards against, one
# level up.
#
# So the reviewer emits the checkbox block itself (the packet asks it to), and this puts the
# block in the right place with a correct heading. The full answer is kept underneath in a
# collapsed block, because "was this actually reviewed" should be answerable later.
#
# It will not accept a ticked box. Only a person ticks, and a reviewer that ticks its own
# findings has marked its own homework.
#
# It also will not accept input that looks TRUNCATED. On 7 September a review was filed from
# a clipboard copied while the CLI was still rendering, and pbpaste took a partly-written
# buffer: whole runs of characters were missing, and the finding line read
# "tracker-export.py:6ths of the body and note" -- unreadable, unfixable, and destined to be
# carried forward for ever because nobody can honestly tick something they cannot read. The
# guard costs one re-copy. Set SKIP_SANITY=1 to file anyway when a terse review is genuinely
# correct and simply does not look like the usual shape.
set -u
cd "$(git rev-parse --show-toplevel)" || exit 1
LOG="docs/reference/review-log.md"
MARK="<!-- NEWEST REVIEW DIRECTLY BELOW -->"

LABEL="${1:-}"
REF="$(git rev-parse --git-dir)/review-packet-ref"

# What the packet ACTUALLY reviewed, not what happens to be HEAD now. A packet built on a
# dirty tree reviews uncommitted work, and filing that against the last commit claims the
# commit was reviewed when it was not.
if [ -n "${2:-}" ]; then
  SHA="$2"
elif [ -f "$REF" ]; then
  M="$(cut -d'|' -f1 "$REF")"; H="$(cut -d'|' -f3 "$REF")"
  case "$M" in
    dirty) SHA="uncommitted-on-$H" ;;
    *)     SHA="$H" ;;
  esac
else
  SHA="$(git log -1 --format=%h)"
  echo "  no packet reference found; filing against HEAD. If the packet reviewed" >&2
  echo "  uncommitted work, this heading will name the wrong thing." >&2
fi

if [ -z "$LABEL" ]; then
  echo "usage: pbpaste | bash tests/review-log-add.sh \"short label\" [sha]" >&2
  echo "       the label is how you will recognise this review in six weeks" >&2
  exit 1
fi
[ -f "$LOG" ] || { echo "no $LOG" >&2; exit 1; }
grep -qF "$MARK" "$LOG" || { echo "no insertion marker in $LOG" >&2; exit 1; }

# The reviewer's answer has to be captured BEFORE python is started: the script itself
# arrives on python's stdin, so anything piped in would already be gone by the time it read.
# Found by running it, which is the only way this class of thing is ever found.
IN="$(mktemp "${TMPDIR:-/tmp}/reviewlog.XXXXXX")"
trap 'rm -f "$IN"' EXIT
cat > "$IN"

python3 - "$LOG" "$MARK" "$LABEL" "$SHA" "$IN" <<'PY'
import datetime, os, re, sys

log, mark, label, sha, inp = sys.argv[1:6]
raw = open(inp, encoding="utf-8").read().rstrip()

if not raw.strip():
    sys.exit("nothing on stdin. Copy the reviewer's answer first, then pipe it in.")

if re.search(r'^\s*- \[[xX]\]', raw, re.M):
    sys.exit("the pasted block contains a TICKED box.\n"
             "Only a person ticks, and a reviewer that ticks its own findings has marked\n"
             "its own homework. Paste it with '- [ ]' and tick by hand once you have seen\n"
             "the fix.")

# Findings: an unticked box plus any indented continuation lines under it.
lines = raw.split("\n")
findings, keep = [], False
for ln in lines:
    if re.match(r'^\s*- \[ \]', ln):
        findings.append(ln.strip()); keep = True
    elif keep and re.match(r'^\s+\S', ln):
        findings.append("      " + ln.strip())
    else:
        keep = False

# ---- looks-truncated guard ------------------------------------------------
if not os.environ.get("SKIP_SANITY"):
    complaints = []
    # every question answered? a partly-copied buffer usually loses the tail.
    missing = [n for n in "12345" if not re.search(r'^\s*%s[.)]' % n, raw, re.M)]
    if missing:
        complaints.append("the answer has no question %s. The packet asks five, so this "
                          "looks like a partial copy." % ", ".join(missing))
    # a finding must name something openable.
    for f in findings:
        if not f.startswith("- [ ]"):
            continue
        if not re.search(r'[\w./-]+\.(py|sh|md|js|json|jsonl|html|yaml)(:\d+)?', f):
            complaints.append("this finding names no file you could open:\n      %s" % f)
        # a line number glued straight onto mid-word text is the signature of a clipboard
        # copied mid-render: ":6ths of the body", ":4atches on substring". Structure alone
        # does not catch it, because the path token in front of it is still valid.
        if re.search(r':\d+[a-z]', f):
            complaints.append("a line number runs straight into a word here, which is what a\n"
                              "      part-copied buffer looks like:\n      %s" % f)
    if complaints:
        sys.exit("this does not look like a whole review:\n  - " +
                 "\n  - ".join(complaints) +
                 "\n\nRe-copy the answer once the CLI has finished printing, and try again."
                 "\nIf it really is fine, SKIP_SANITY=1 pbpaste | bash tests/review-log-add.sh ...")

today = datetime.date.today().isoformat()
out = ["## %s — %s — %s" % (today, sha, label), ""]
if findings:
    out += findings
else:
    out += ["Nothing found. Recorded because a log of only non-empty reviews is a biased "
            "log, and because \"has this been reviewed at all\" is a question worth being "
            "able to answer."]
out += ["", "<details><summary>the review, as it came back</summary>", "",
        "```", raw, "```", "", "</details>", "", "---", ""]

s = open(log, encoding="utf-8").read()
s = s.replace(mark, mark + "\n\n" + "\n".join(out), 1)
open(log, "w", encoding="utf-8").write(s)
print("  filed: %s — %s — %s" % (today, sha, label))
print("  %d finding(s) recorded as unticked" % len(
    [f for f in findings if f.startswith("- [ ]")]))
PY
rc=$?
[ "$rc" = 0 ] || exit "$rc"

echo
echo "  next:  bash tests/review-carry.sh | pbcopy"
echo "         paste into the SAME session, then tick by hand what it shows you was fixed."
