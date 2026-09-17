#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Enforce docs/INDEX.md.
#
# Four checks, each of which corresponds to something that actually went wrong:
#
#   1. DANGLING PATHS. A file named in INDEX.md or OPEN.md that does not exist.
#      OPEN.md pointed at docs/delivery-platform.md and docs/tester-attrition.md for a
#      week; neither existed.
#   2. ORPHANED DOCS. A file under docs/ that INDEX.md does not list. This is what stops
#      the index rotting: a new document has to be indexed or the build fails.
#   3. PLACEHOLDERS IN TESTER-FACING FILES. [CONTACT] reaching a volunteer is not a typo,
#      it is a broken promise about withdrawal.
#   4. THE PARTICIPATION NOTE COPIES DIVERGING. Two copies exist because the kit runs
#      offline. The one testers read is the kit copy.
#
# What this deliberately does NOT check: whether a document is TRUE. Nothing mechanical
# can. It checks that claimed things exist, which is the failure mode that has actually
# bitten.
#
# EXIT CODES
#   0  clean
#   1  structural failure: something claimed does not exist, or two copies diverged.
#      This fails the build, because it means a document is lying.
#   2  placeholders remain in tester-facing text. Loud, printed on every run, and NOT
#      build-failing -- the contact address and return route are decisions Ranaji has to
#      make, and blocking every commit on them would only teach us to skip the suite.
#      It DOES block recruitment, which is the thing it is actually guarding.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
fail=0; soft=0

# ---- 1. dangling paths ------------------------------------------------------
paths=$(grep -ohE '`[A-Za-z_][A-Za-z0-9_./-]*\.(md|sh|py|js|html|jsonl|json|txt)`' \
          "$ROOT/docs/INDEX.md" "$ROOT/OPEN.md" "$ROOT/../OPEN.md" 2>/dev/null \
        | tr -d '`' | sort -u)
missing=""; private=""
for p in $paths; do
  case "$p" in
    */*) ;;                       # a real path
    *) continue ;;                # a bare filename, too ambiguous to resolve
  esac
  case "$p" in _superseded/*|library/*) continue ;; esac
  # A gitignored path is deliberately private -- the tracker and its export carry
  # third-party names and never enter git. It exists on this machine and will NOT exist
  # in a clone, so "missing" here would fail the build for a stranger and prove nothing.
  # Name it instead of checking it.
  if git -C "$ROOT" check-ignore -q "$p" 2>/dev/null; then
    private="$private $p"; continue
  fi
  [ -e "$ROOT/$p" ] || [ -e "$ROOT/../$p" ] || missing="$missing $p"
done
if [ -n "$missing" ]; then
  echo "  DANGLING: named in an index but not on disk:"
  for p in $missing; do echo "      $p"; done
  fail=1
fi
if [ -n "$private" ]; then
  echo "  PRIVATE, so not checked here (untracked by design, absent in a clone):"
  for p in $private; do echo "      $p"; done
fi

# ---- 2. orphaned docs -------------------------------------------------------
orphans=""
while IFS= read -r f; do
  rel="${f#$ROOT/}"
  case "$rel" in docs/INDEX.md) continue ;; esac
  grep -qF "$rel" "$ROOT/docs/INDEX.md" || orphans="$orphans $rel"
done < <(find "$ROOT/docs" -name '*.md' -type f)
if [ -n "$orphans" ]; then
  echo "  ORPHANED: under docs/ but not listed in docs/INDEX.md:"
  for p in $orphans; do echo "      $p"; done
  echo "      Add it to the index, or move it out of docs/."
  fail=1
fi

# ---- 3. placeholders in anything a tester reads -----------------------------
holders=$(grep -rn '\[CONTACT\]\|\[RETURN ROUTE\|\[TO BE DECIDED' \
            "$ROOT/bench-kit" "$ROOT/docs/reference/participation-note.md" 2>/dev/null || true)
if [ -n "$holders" ]; then
  echo "  PLACEHOLDERS still in tester-facing text:"
  printf '%s\n' "$holders" | sed "s|$ROOT/|      |"
  echo "      These MUST be filled before anyone is invited. RECRUITMENT IS BLOCKED"
  echo "      until they are. Not build-failing: they are decisions, not defects."
  soft=1
fi

# ---- 4. instruction files referenced from editor settings must exist --------
# VS Code does not warn when a { "file": ... } instruction points at nothing. Copilot
# would review with only the inline rules and say so to nobody. Same "passes because it
# did not run" shape the suite exists to catch.
if [ -f "$ROOT/.vscode/settings.json" ]; then
  refs=$(grep -oE '"file"[[:space:]]*:[[:space:]]*"[^"]+"' "$ROOT/.vscode/settings.json" \
         | sed -E 's/.*"file"[[:space:]]*:[[:space:]]*"([^"]+)".*/\1/' | sort -u)
  gone=""
  for r in $refs; do [ -e "$ROOT/$r" ] || gone="$gone $r"; done
  if [ -n "$gone" ]; then
    echo "  BROKEN EDITOR INSTRUCTION: .vscode/settings.json points at a file that is gone:"
    for r in $gone; do echo "      $r"; done
    echo "      Copilot would silently review with fewer rules than you think."
    fail=1
  fi
fi

# ---- 5. the two participation notes must agree ------------------------------
A="$ROOT/docs/reference/participation-note.md"; B="$ROOT/bench-kit/participation-note.md"
if [ -f "$A" ] && [ -f "$B" ]; then
  if ! cmp -s "$A" "$B"; then
    echo "  DIVERGED: docs/reference/participation-note.md and bench-kit/participation-note.md"
    echo "      The kit copy is the one testers read. Copy the canonical one over it:"
    echo "      cp docs/reference/participation-note.md bench-kit/participation-note.md"
    fail=1
  fi
else
  echo "  MISSING one of the participation-note copies"; fail=1
fi

# ---- 6. OPEN.md and its in-repo snapshot must agree -------------------------
# OPEN.md is generated from the tracker and copied into the repo. If one side edits the
# snapshot directly, the tracker silently stops being the record. This is the same failure
# as the two participation notes, one level up.
O="$ROOT/../OPEN.md"; S="$ROOT/docs/open-items-snapshot.md"
if [ -f "$O" ] && [ -f "$S" ] && ! cmp -s "$O" "$S"; then
  echo "  DIVERGED: OPEN.md and docs/open-items-snapshot.md"
  echo "      The snapshot is GENERATED. Do not edit it directly -- change the tracker,"
  echo "      export, then: cp ../OPEN.md docs/open-items-snapshot.md"
  fail=1
fi

# ---- 7. duplicate paths in docs/INDEX.md -------------------------------------
dup_paths=$(grep -oE '^\|[[:space:]]*`[^`]+`' "$ROOT/docs/INDEX.md" | tr -d '|` ' | sort | uniq -d)
if [ -n "$dup_paths" ]; then
  echo "  DUPLICATE PATHS in docs/INDEX.md:"
  for p in $dup_paths; do echo "      $p"; done
  echo "      Each file must appear in docs/INDEX.md at most once."
  fail=1
fi

if [ "$fail" = 0 ] && [ "$soft" = 0 ]; then
  n=$(find "$ROOT/docs" -name '*.md' | wc -l | tr -d ' ')
  echo "  $n documents, all indexed; no dangling paths; no placeholders in tester text"
elif [ "$fail" = 0 ]; then
  n=$(find "$ROOT/docs" -name '*.md' | wc -l | tr -d ' ')
  echo "  $n documents, all indexed; no dangling paths. Placeholders above."
fi
[ "$fail" = 1 ] && exit 1
[ "$soft" = 1 ] && exit 2
exit 0
