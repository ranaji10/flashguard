# Repair task, 14 September. Four defects, one decision.

The build is close. The blind review found five things; one is already fixed, one needs a
ruling from Ranaji, and three are real. One of those three is a **wrong value written to the
two fields the verifier most depends on**, on the platform most testers will use, and it was
covered by a test that could not fail.

Read the reproductions before writing code. They are commands, not opinions.

---

## 1. BLOCKING. CRLF from `adb shell` silently changes the answer.

`adb shell` on Windows prints CRLF. `bench-kit/scripts/02-android.sh` strips it per value
with `tr -d '\r\n'`. The raw-paste path in `START-HERE.html:774` does `t.trim()` only, which
trims the ends of the blob and leaves a `\r` on every interior line.

Reproduce, from the repository root:

```
F=tests/android/real-nothing-phone-2026-08-29.props
grep -v '^#!' $F | bash bench-kit/scripts/derive.sh | grep -E 'partition_scheme|bootloader_state'
grep -v '^#!' $F | sed 's/$/\r/' | bash bench-kit/scripts/derive.sh | grep -E 'partition_scheme|bootloader_state'
```

What comes back:

```
LF    partition_scheme  virtual_A/B      bootloader_state  locked
CRLF  partition_scheme  A/B              bootloader_state  unknown
```

`virtual_A/B` became `A/B`. That is not an abstention, it is a **different confident answer**
about a recipe-matching field. And a locked bootloader became unestablished, which throws
away an `unsafe` verdict the device had earned.

**Fix:** normalise line endings where the text is captured, in `tryParse` at
`START-HERE.html:768`, before the leak check and before storing: `t.replace(/\r\n?/g, "\n")`.
Normalise at the boundary, once, not in `derive.sh` and not in two places.

## 2. BLOCKING. The cmd.exe fallback produces a record that means nothing.

`START-HERE.html:762` offers nineteen bare `adb shell getprop <key>` lines "if running cmd.exe
without PowerShell loop support". Each of those prints a **value with no key**. Reproduce:

```
grep -v '^#!' tests/android/real-nothing-phone-2026-08-29.props | cut -d= -f2- \
  | bash bench-kit/scripts/derive.sh | grep -E 'partition_scheme|bootloader_state|android_version'
```

Every field comes back `unknown`. The record is then shaped exactly like
`tests/android/empty-everything.props`, which is the fixture for *a phone that answered
nothing*. A tester who followed the documented instructions produces a record indistinguishable
from a dead device, and nothing anywhere says otherwise.

**Fix, and prefer the first:** delete the fallback. The main command already runs the loop
**inside `adb shell`**, on the phone's own shell, so PowerShell and cmd never parse anything
and the fallback is solving a problem that does not exist. If you keep it, the pasted text must
be **refused** with a message naming what is wrong, never stored.

## 3. BLOCKING. `tests/test-android-raw-agreement.sh:23` cannot fail.

```
bash_raw=$(grep -v '^#!' "$f")
raw_paste="$bash_raw"          # line 23
```

It asserts `derive.sh(x) == derive.sh(x)`. It proves `derive.sh` is deterministic and nothing
else. The two routes do not differ in the derivation, they differ in **the shape of the text
that arrives**, which is the thing this test does not touch. It would have caught defect 1 in
one run.

**Fix.** For each `tests/android/*.props`, derive the canonical text, then derive each of these
and assert:

- **CRLF** (`sed 's/$/\r/'`) — must MATCH the canonical derivation after the page's normaliser.
- **Bare values, no keys** (`cut -d= -f2-`) — must be REFUSED, not silently derived. If you took
  the delete option in defect 2, assert instead that the page no longer offers this shape.
- **Blank lines and leading whitespace interleaved** — must match.
- **Keys in a different order** — must match.

Then plant a discrepancy, watch the test fail with a message that names the shape, and restore.
A test that has never failed is a comment. That is why this one was worth nothing.

## 4. Pending records claim seventeen things they have not established.

`START-HERE.html:914` writes `android_derivation: "pending"` and then seventeen fields as
`"unknown"`. The schema is explicit that `unknown` means *the field applies and could not be
established read-only* — a final answer about the hardware. These are not that. They are "not
computed yet", and the record cannot tell the two apart. That is the exact three-way absence
ambiguity `data/schema.md` lines 37 to 43 exist to prevent, and it is now in the newest code.

The blind reviewer's own note is right: it does not produce a false safe today, because the
verifier abstains on `unknown`. It pollutes the matrix the first time anything treats
`unknown` as ground truth.

**Fix, three parts:**
- When derivation is pending, emit **only** `android_raw` and `android_derivation: "pending"`.
  Do not emit the derived keys at all. A missing key is not a value; a wrong one is.
- Document `android_raw` and `android_derivation` in `data/schema.md`, in the same shape as the
  other fields, and state that `pending` is the only non-final value the record may carry.
- Add a gate: whatever admits a record to the matrix must **refuse** one carrying
  `android_derivation: "pending"` until it has been derived. Nothing outside START-HERE.html
  currently knows these fields exist, which is how a latent defect stays latent.

## 5. The Ubuntu choice is offered and does not work.

`scrPlatform` at line 690 offers **Live Ubuntu USB stick**, and `scrRoutePlatform` at line 706
sends it straight to `scrAndroidBash("linux_live")`. The two screens that tell a tester how to
make a stick and boot it, `scrPrep` and `scrBootUp` at lines 785 and 797, are called by nothing
except each other. The comment above them says "Accessible if requested" and no code path
requests them.

So a tester who picks the Ubuntu route is told to run a bash script on a machine they have not
been told how to create. This is a hole, not a stale comment.

**Fix:** route `ubuntu_live` through `scrPrep` → `scrBootUp` → `scrAndroidBash("linux_live")`,
and correct the comment to say what is true. If you would rather drop the Ubuntu route for
Tuesday, remove it from the picker as well, so nothing is offered that does not work.

---

## Ranaji's decision, not yours: finding 1

`tests/webusb-fixtures/18d1-4ee2.desc:10` reads `product YUPIK-QRD <stripped>`. The finding as
filed says the file "stores a device serial (`_SN:<stripped>`)". It does not. The serial is
gone; `<stripped>` is the redaction marker, and it is the evidence that the masker ran on the
device that caused the fourteen-day leak. Removing it would remove the proof.

Leave the fixture alone. Ranaji ticks the finding with the wording corrected, or rules
otherwise. Do not change the fixture on your own judgement.

---

## Order of work, because Tuesday is the day after tomorrow

1, 2 and 3 together — they are one defect and its missing test. Then 5, which is fifteen
minutes. Then 4, which does not block the hackerspace but must land before any record merges.

## When you are done

`bash tests/all.sh` at its usual soft exit 2, nothing newly failing, plus:
`tests/check-portability.sh` green (bash 3.2, which is what macOS ships).
Zip `bench-kit/`, unzip somewhere new, double-click START-HERE.html, and run a real phone
through **the Windows raw-paste path specifically**, since that is the one that was wrong.

Then `bash tests/handoff.sh`, and `bash tests/review-packet.sh` to a fresh reviewing session in
a different model family. Give it the packet and nothing else.
