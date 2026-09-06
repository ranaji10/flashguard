# Sync: what "sync" means, and which copy wins

*The tracker exists in two places on purpose. This is the rule that stops them lying to
each other.*

## The two copies

| | Where | Good for | Cannot |
|---|---|---|---|
| **The file** | `project/docs/tracker/open-items.html` | Copilot reads and writes it; it is in git, so every change has a diff and a history | Be opened from a phone |
| **The published page** | <https://claude.ai/code/artifact/bbac4a10-81b5-49bb-b206-46e4cbe6d303> | Typing notes from anywhere, including a phone; Save publishes to every device | Be read by Copilot, or by anything in this repository |

They are the **same source**. The file is what gets published; the published page rebuilds
that same file when Save is pressed. They diverge the moment one side is edited alone,
and neither can detect that on its own — the repository cannot reach claude.ai and the
page cannot reach the repository.

**So the rule is: one side at a time, and export before switching.**

## The third copy, which was invisible

There was a third copy nobody had counted: **the browser's own.** The page keeps what you
type in `localStorage` so a note survives a closed tab before Save is pressed. That is
worth having. What it did was worse than that.

`localApply()` wrote its stored statuses and notes over the freshly loaded data for every
item it had an entry for, and the "unpublished" flag only decided whether a message was
shown. So a browser that had ever touched this page kept quietly re-applying its old
snapshot over every version published afterwards. The same bytes rendered two different
ways, and the browser won every argument with the file without saying so.

Fixed 7 September:

- **Opened from a file, browser storage is off entirely.** Double-click the file and you
  see the file. Nothing is read, nothing is written.
- **On the published page, stored edits carry the version they were made against** and are
  re-applied only when that still matches. When it does not, the page shows what was
  published, says how many unpublished changes this browser is holding, and gives you two
  buttons: *Put my changes back*, or *Discard them*. Nothing merges behind anyone's back.
- **Both copies print a version fingerprint** in the banner, and `OPEN.md` carries the same
  string in its header. Three places compute it independently — the page in the browser,
  `tests/tracker-export.py`, and `tests/check-tracker.sh` — so "are these the same version"
  is answered by looking, not by trusting.

## How to tell, in five seconds

Open both. Compare the `version` in the banner.

| What you see | What it means | What to do |
|---|---|---|
| Same fingerprint | The two copies agree | Nothing |
| Page is behind the file | The file was edited and not republished | Ask a Claude session to republish from the file |
| File is behind the page | Notes were typed and saved on the page | Export from the page, or ask a session to read it back |
| A yellow banner offering two buttons | This browser is holding unpublished edits made against an older version | Read what it says, then choose |

Opened from Finder the page works fully except Save, which says so plainly rather than
failing silently. Export still produces the markdown.

## "sync", said to Copilot

One word, and it means exactly this:

> Read `docs/tracker/open-items.html`. For every item in the `appdata` JSON that has a
> `note`, decide whether the note has overtaken the item body `d`. Where it has, rewrite
> `d` so it states where the item stands NOW — the decision if one was made, what it
> changed, and what remains — and set `touched` to today. Never edit or delete a `note`:
> notes are Ranaji's words and they are the trail, not the status. Then run
> `python3 tests/tracker-export.py` and commit.

The long form of that instruction lives in `.github/copilot-instructions.md` so the word
alone is enough.

**What "update the pointer" means.** The body of an item is not the question that opened
it. It is the current position. An item whose body still reads like the original question,
with the answer only in the note underneath, has not been synced — it has been annotated.
The test: if the note were deleted, would the body still be true and useful? If not, the
body is stale.

## "sync", said to a Claude session

Same word, different mechanics, because a Claude session can reach the published page and
Copilot cannot. It reads the artifact, merges anything typed there, republishes, writes the
file back into the repository, and regenerates `OPEN.md`.

Which one to ask depends on where the notes were typed. Notes typed on a phone are on the
published page and only a Claude session can fetch them. Notes typed in VS Code are in the
file and Copilot is already there.

## Generated files: do not edit

- `OPEN.md` (at the top of `Repurpose/`) — generated
- `project/docs/open-items-snapshot.md` — generated, and identical to it

Both come from `python3 tests/tracker-export.py`. `tests/check-index.sh` fails the build
when they disagree, because a hand-edited snapshot means the tracker has quietly stopped
being the record. Edit the tracker; run the exporter.

## The failure this is designed against

On 30 August seven of Ranaji's notes were overwritten with an assistant's summaries of
them, and it was caught only because he asked for a comparison against an old copy of the
file. On 6 September an audit found eleven decisions that lived in conversation and in no
file at all, and three files claiming to cover work that had not happened when they were
written.

Both failures have the same shape: **something was described rather than recorded, and
nothing checked.** The rules above are narrow on purpose. Notes are never rewritten.
Bodies are always rewritten. Generated files are never hand-edited. Everything else is
detail.
