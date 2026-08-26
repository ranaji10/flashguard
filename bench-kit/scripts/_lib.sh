# SPDX-License-Identifier: GPL-3.0-or-later
# shared helpers. sourced, not run.

# escape a string for embedding in JSON
jesc() { printf '%s' "$1" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g' -e 's/\t/ /g' | tr -d '\r\n'; }

# hand the capture line to the browser with as little user effort as possible
emit() {
  line="$1"
  copied=""
  if command -v wl-copy >/dev/null 2>&1;   then printf '%s' "$line" | wl-copy 2>/dev/null && copied="yes"
  elif command -v xclip >/dev/null 2>&1;   then printf '%s' "$line" | xclip -selection clipboard 2>/dev/null && copied="yes"
  elif command -v xsel  >/dev/null 2>&1;   then printf '%s' "$line" | xsel --clipboard 2>/dev/null && copied="yes"
  fi
  mkdir -p "$HOME/bench"
  printf '%s\n' "$line" > "$HOME/bench/capture-latest.txt"

  echo
  echo "============================================================"
  if [ -n "$copied" ]; then
    echo "  COPIED TO CLIPBOARD."
    echo "  Go to the browser and click Paste. Nothing else to do."
  else
    echo "  Select the line below, copy it, paste it in the browser."
    echo "  (In the terminal: select with the mouse, then Ctrl+Shift+C)"
  fi
  echo "============================================================"
  echo
  echo "$line"
  echo
}
