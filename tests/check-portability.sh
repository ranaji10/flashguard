#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Reject bash 4+ constructs in the kit.
#
# The kit runs in two places that do not agree: an Ubuntu live session (bash 5)
# and the authoring Mac (bash 3.2, which Apple has shipped since 2007 for licence
# reasons and will not update). A script written and tested only on Linux can use
# a construct that dies on the Mac, and `bash -n` will not notice, because these
# are runtime failures, not syntax errors.
#
# That happened on 29 Aug: derive.sh used `declare -A`, passed every Linux check,
# and failed on the first real run. Volunteers will bring machines we have never
# seen, so this is not a one-off.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
fail=0

check(){ # pattern, why
  local pat="$1" why="$2"
  local hits
  hits=$(grep -rnE "$pat" "$HERE/../bench-kit/scripts" "$HERE"/*.sh 2>/dev/null \
         | grep -vE '^[^:]+:[0-9]+:[[:space:]]*#' | grep -v 'check-portability' || true)
  if [ -n "$hits" ]; then
    echo "  BANNED: $why"
    printf '%s\n' "$hits" | sed 's/^/      /'
    fail=1
  fi
}

check 'declare +-[a-zA-Z]*A'    'declare -A (associative arrays) needs bash 4'
check 'local +-[a-zA-Z]*A'      'local -A needs bash 4'
check '\$\{[A-Za-z_][A-Za-z0-9_]*(,,|\^\^)' 'case conversion ${v,,} / ${v^^} needs bash 4'
check '\bmapfile\b|\breadarray\b' 'mapfile / readarray need bash 4'
check '\bcoproc\b'              'coproc needs bash 4'
check ';;&'                     ';;& in case needs bash 4'
check '&>>'                     '&>> needs bash 4'

if [ "$fail" = 0 ]; then
  echo "  no bash-4-only constructs (bash 3.2 hosts are supported)"
  echo "  running bash: ${BASH_VERSION:-unknown}"
fi
exit "$fail"
