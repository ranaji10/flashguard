# Batch 2 of 4, 16 September. The Windows command block, and the guard that was removed.

Run this batch **after batch 1 is committed**, because both touch `bench-kit/START-HERE.html`.

The first defect here is the one the eight-paste-shape verification could not have caught,
and it is worth saying why: that work proved the **parser** handles whatever arrives. It
never asked whether the **command we hand out** produces anything on the platform we hand it
to. The mechanism was checked and the thing it was pointed at was not.

---

## 1. BLOCKING. The command block offered to Windows testers is eaten by PowerShell.

`scrAndroidRaw` is the screen every Windows tester lands on. Its heading says
`PowerShell / cmd`, and the block it offers is:

```
START-HERE.html:768
adb shell "for p in ro.product.manufacturer ... ; do echo $p=$(getprop $p); done"
```

That string is wrapped in **double quotes**. In PowerShell a double-quoted string is
expanded before the command runs: `$p` is substituted with the value of a PowerShell
variable named `p`, which does not exist and expands to empty, and `$(getprop $p)` is a
subexpression that PowerShell executes **on Windows**, where `getprop` is not a command.

In `cmd.exe` the same string is passed through untouched, because `cmd` does not expand
`$`, so the device shell receives it intact and it works.

So the heading claims two shells and the block works in one of them. PowerShell is the
default shell on current Windows and is the one the heading names first.

**Do not fix this by guessing at escapes.** Fix it by asking, which is what the platform
picker already exists to do.

**Fix:**

1. Split the Windows branch of `scrRoutePlatform` into two: PowerShell and cmd. A small
   second question on the same screen is fine; a separate screen is also fine. Whichever you
   choose, the answer must be recorded, because it is the shell the tester actually used.
2. Give PowerShell a **single-quoted** command string. PowerShell treats a single-quoted
   string as a literal and passes it to `adb` as one argument, so the loop reaches the
   device shell unexpanded.
3. Leave the existing double-quoted block on the cmd branch, where it already works.
4. Keep both blocks reading the **same nineteen properties in the same order**. If the two
   diverge, the two shells produce different records and nothing will notice.

**Prove it, and this is the part that matters:** a claim about PowerShell cannot be settled
by reading the file. Ranaji has a Windows machine in the test plan. Add a short note at the
top of your summary naming the two exact strings you produced, so both can be run once on a
real Windows box before ten strangers see them. If you cannot test it, say so plainly rather
than asserting it works.

**Also fix the heading.** Whatever the screen ends up offering, the kicker must name the one
shell that block is for. `PowerShell / cmd` above a block that works in one of them is the
same class of untrue label as a `host_platform` field that says `ubuntu_live` about a macOS
capture.

---

## 2. NOT BLOCKING, five minutes. Put the offer guard back.

A test used to grep `START-HERE.html` and assert that the bare
`adb shell getprop <key>` block had not returned. It was deleted when
`tests/test-android-raw-agreement.sh` was rewritten on 14 September, and nothing replaced it.

What is still protected: `isValidRawProps` refuses bare-value text at paste time, which is
strictly better at the thing that matters, because it catches bad input arriving by any
route rather than one.

What is no longer protected: the page **offering** instructions that produce a shape the page
will then refuse. That is a user-experience failure rather than a data failure. Nothing wrong
enters the matrix; a tester simply follows the instructions, pastes, and is told the text
contains no properties.

**Fix:** restore the one-line grep in the bash test. Assert that no line of
`bench-kit/START-HERE.html` offers a `getprop` invocation whose output would be bare values
with no keys. Make the assertion specific enough that it fails if such a block returns, and
loose enough that it does not fire on the loop forms, which do print `key=value`.

**Prove it:** paste a bare-value block into the file, run the test, watch it fail, remove it,
watch it pass.

---

## What "done" means for this batch

- `bash tests/all.sh` runs and nothing that passed before fails now.
- The two PowerShell and cmd strings are stated verbatim in your summary for a real Windows
  test, and you have said clearly whether you were able to run either of them.
- The restored guard was proved to fail on a planted bare-value block.
- No file outside `bench-kit/START-HERE.html` and `tests/test-android-raw-agreement.sh` has
  changed.
- `bash tests/check-public-safe.sh` still passes, and no absolute path or home directory
  appears in anything you touched.

Do not report build status in a summary. Ranaji runs the suite himself.
