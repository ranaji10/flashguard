# Batch 2b, 16 September. One field, and it is the one batch 2 quietly widened.

Small. Run it before batch 3, because both touch `data/schema.md`.

---

## The defect

Batch 2 split the Windows branch into PowerShell and Command Prompt, which was right and is
working. It also writes the answer into `S.host_platform`:

```
bench-kit/START-HERE.html   S.host_platform = plat;   // "windows_powershell" | "windows_cmd"
```

`data/schema.md` defines that field as an operating system, and enumerates its values:

```
data/schema.md:69    "host_platform": "macos | windows | ubuntu_live | ubuntu_installed | linux_other | not_stated"
data/schema.md:170   The operating system platform explicitly selected by the tester
```

Neither `windows_powershell` nor `windows_cmd` is in that list. **So every Windows record from
now on carries a value no document defines, and nothing checks it** — `data/merge.py` validates
several things and not this one.

No false safe: the verifier never reads `host_platform`. But this is the field that exists so a
record captured by a route the shipped product will not have can be told apart from one that
can, and it is now carrying values nobody wrote down.

## The fix, and it is a naming decision rather than a widening

`host_platform` means an operating system. `windows_powershell` is an operating system **and** a
shell. Putting the shell into the OS field conflates two things, which is the family of defect
this repository has paid for repeatedly: one identifier under two names, a field that means one
thing on Monday and one and a half on Tuesday.

**So add a field rather than widen one:**

1. `host_platform` goes back to `windows` for both Windows branches. Its enumerated values are
   unchanged and `data/schema.md` needs no edit to that line.
2. Add `host_shell`, recorded only where a shell was actually chosen: `powershell | cmd |
   not_applicable`. Not `unknown` — on macOS or Linux the question was never asked and cannot
   apply, which is what `not_applicable` means in this schema. Define it in `data/schema.md`
   beside `host_platform`, and say why it exists in one sentence: the quoting differs between
   the two Windows shells and the command handed to the tester differs with it, so a record
   that does not say which shell produced it cannot be re-derived with confidence.
3. `bench-kit/START-HERE.html` keeps the two-button screen exactly as it is and simply writes
   the two fields instead of one.

**Do not invent a third Windows value later.** If a shell appears that is neither, it is
`not_applicable` plus a note, and somebody decides what it means before it becomes a value.

## Tests

- A record captured on the PowerShell branch carries `host_platform: "windows"` and
  `host_shell: "powershell"`.
- A record captured on the cmd branch carries `host_platform: "windows"` and `host_shell: "cmd"`.
- A record captured on macOS or Linux carries `host_shell: "not_applicable"`, never `unknown`
  and never absent.
- **And the one that would have caught this in the first place:** a test asserting that every
  `host_platform` value a record can carry is one `data/schema.md` enumerates. Write it against
  the schema text rather than a copy of the list, so the two cannot drift.

That last test is the point of the batch. The defect is small; the reason it reached a commit is
that nothing compares what the page writes with what the schema declares.

---

## If you would rather just widen the list

Add `windows_powershell | windows_cmd` to the enumeration in `data/schema.md` and stop. It is
one line and it is defensible. The cost, stated so it is chosen rather than discovered: the
field then means OS-or-OS-plus-shell depending on the row, and anything that later groups
records by platform has to know that `windows`, `windows_powershell` and `windows_cmd` are the
same operating system. Ranaji decides; the producer does not.

---

## What "done" means for this batch

- `bash tests/all.sh` runs and nothing that passed before fails now.
- The schema-agreement test was proved to fail by planting an undeclared value.
- No file outside `bench-kit/START-HERE.html`, `data/schema.md` and the tests changed.
- `bash tests/check-public-safe.sh` still passes.

Do not report build status in a summary. Ranaji runs the suite himself.
