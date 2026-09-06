# Flashguard

Flashguard decides whether a provisioning recipe is safe for a specific device, **without
executing it**. A wrong "safe" can brick someone's phone. That single fact orders every rule
below.

`CLAUDE.md` is the full rulebook and the source of truth. This file is the short version.
`docs/INDEX.md` maps every decision to the file that holds it.

## Never

- Write to, flash, erase, unlock or modify a device. Never generate `fastboot
  flash|erase|format|oem|flashing|boot|update|set_active`, `adb root|remount|disable-verity`,
  `dd`, `mkfs`, `parted`.
- Read or store a serial number, IMEI, IMSI, MAC, ICCID or Android ID. Use `adb get-state`,
  never `adb devices`. Strip `iSerial` from `lsusb -v`. Query an explicit property allowlist,
  never a bare `getprop` dump.
- Turn an absent value into a confident one. Missing evidence stays `unknown`.
- Use `declare -A`, `mapfile`, `readarray`, `${v,,}`, `${v^^}` or `coproc`. Shell must run on
  **bash 3.2**, which macOS ships.
- Use machine-learning vocabulary. Nothing here is trained or inferred. `classify.sh` is a
  deterministic decision procedure; `classifier_confidence` is a hand-assigned constant.
- Copy anything from `../library/`. It is borrowed material under other licences and must
  never enter this GPL repository.

## Always

- Keep `classify.sh`, `derive.sh` and the verifier **pure**: text in, result out. No device
  I/O, no network, no filesystem, no global state.
- Add a test fixture in the same commit as a new device class or vendor.
- Run `bash tests/all.sh` before committing.
- Prefer abstaining and saying so over guessing.

## Scope

This repository is **one thing: the recipe verifier**. Capability inference, path generation,
a platform, an app, a website, a probability score — all out of scope. They belong to
"RePurpose", a separate future ambition. Over-scoping is the most common reason funding
applications like this one are rejected.

## Current state

The v0.1 pure verifier exists at `flashguard/verify.py`, and five independently authored
recipes exist under `data/recipes/`. The corpus replay reports five `cannot-verify` results,
zero decided results, and zero false safes. V0.1 has no defensible `safe` case; see
`docs/reasoning/safe-case.md`. Do not extend the bench kit unless a tester is blocked.

## Nothing is done until a command proves it

- **Write the failing check first.** Before implementing, produce a test that fails now and
  passes only when the work is correct. Run it. Show it failing. A claim with no executable
  check behind it is not a claim, it is a hope.
- **End every piece of work with the command that proves it**, and its output. If no command
  could fail were the work absent, say so rather than reporting completion.
- **Tense is not decoration.** Describe what EXISTS in the present tense and what does not in
  the conditional. `verify()` does not exist. Never write a docstring, comment, README line
  or commit message that describes unimplemented behaviour as though it works — a document
  that describes a thing convincingly is how this project already lost a week: a run log
  claimed to cover work it predated, and nothing checked. The same rule runs backwards:
  `verify()` DOES exist now, and any line still saying it does not is a stale claim to fix,
  not a comment to leave alone.
- **Never mark an item done in `OPEN.md` or `docs/INDEX.md`** on the strength of having
  written about it.

## Disagreements are settled by the suite, or escalated — never by picking

When you and a reviewer disagree, or you are unsure between two defensible options:

1. **If a test could settle it, write the test.** That is the answer, not a discussion.
2. **If no test can settle it, mark it and stop.** Do not choose quietly and move on.

```
# DISPUTED: should `variant` be a verifier concept or a placeholder?
#   position A: a verifier concept -- upstream configs expose device-code aliases
#   position B: a placeholder -- no observed device reports a variant
#   settles it: no test can. Needs a decision from Ranaji.
```

`tests/check-disputed.sh` collects these and reports them at exit 2, loud and not
build-failing. A marker whose "settles it" line names a test you could have written is
laziness, not honesty: write the test.

Never resolve a disagreement by rewriting the question, and never mark something DISPUTED
to avoid doing the work.

## "sync" — the one-word command

The tracker source is `docs/tracker/open-items.html`. Its data is a single
`<script id="appdata" type="application/json">` block, so it can be read and rewritten
without parsing HTML. When Ranaji says **sync**, and nothing else:

1. Read `docs/tracker/open-items.html`.
2. For every item in `appdata` that carries a `note`, decide whether the note has overtaken
   the item body `d`.
3. Where it has, **rewrite `d`** so it states where the item stands NOW: the decision if one
   was made, what it changed, and what remains. Set `touched` to today's date, and set
   `state.updated` to the same date so the "Moved this sweep" filter works.
4. **Never edit, summarise or delete a `note`.** Notes are Ranaji's own words and they are the
   trail, not the status. Seven of them were once overwritten with an assistant's summaries
   and it was caught only by accident. Append to a note, dated, or leave it alone.
5. Run `python3 tests/tracker-export.py`, then `bash tests/all.sh`, then commit.

The test for a synced item: **if the note were deleted, would the body still be true and
useful?** An item whose body still reads like the original question, with the answer only in
the note underneath, has been annotated rather than synced.

Full rules, including what the published copy at claude.ai can and cannot do, are in
`docs/reference/sync-protocol.md`.

## Generated files — never edit directly

- `OPEN.md` and `docs/open-items-snapshot.md` are both generated by
  `python3 tests/tracker-export.py` from `docs/tracker/open-items.html`. Change the tracker,
  not either file. The suite fails if the two drift apart.
- `data/device-matrix.jsonl` is generated by `data/merge.py` from `data/contributions/`.
  Editing it directly loses provenance.

## Being reviewed

Your work is reviewed by a session that has never seen this conversation, and that is
deliberate. Do not write it a summary — a reviewer given the producer's account of the
work grades the account. Commit, do not push, then:

    bash tests/review-packet.sh | pbcopy

That is the whole handoff. Findings come back into `docs/reference/review-log.md` as
unticked boxes, and `bash tests/review-carry.sh` re-surfaces them in later reviews until
someone ticks them by hand.

## Handing back to a Claude session

Run `bash tests/handoff.sh` and paste its output. Do not describe what you did in prose —
hand over the commit. See `docs/reference/handoff.md`.

## Two rules that are easy to break by accident

- **Hardware facts are read, never recalled.** Before writing any command containing a disk
  name, mount path or device model, read `docs/reference/bench-hardware.md`.
- **A decision is not made until it is in a file.** Write it where it will be read, add it to
  `docs/INDEX.md`, and run the suite. `tests/check-index.sh` fails on a document that is not
  indexed.
