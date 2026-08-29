# How defects get caught before a device is plugged in

*Written 29 August 2026, after the first bench run produced two classifier defects
that were both found by hand, days late, in data already collected.*

## What went wrong, precisely

Two defects, one run:

1. **v1 called every USB class `0x06` device a camera.** Class `0x06` is shared by
   PTP (cameras) and MTP (phones in file-transfer mode). Nine of thirteen records
   were wrong.
2. **v2 read only the first USB interface.** A phone with debugging on is a
   composite device: interface 0 is MTP, and the ADB interface is further down. The
   one phone that was configured correctly for the whole run was recorded as a
   camera four times.

Both were visible in data that had already been collected. Neither was caught by
running the tool, because running the tool produced a confident answer either way.
**A classifier with no ground truth to check against does not fail; it just lies
quietly.**

## The structural fix

Classification is now a **pure function over text**, in `bench-kit/scripts/classify.sh`:
`lsusb -v` output on stdin, key/value lines on stdout, no device, no I/O, no side
effects. `01-detect.sh` does the device I/O and the printing and decides nothing.

This is the same shape the verifier itself must have — `verify(fingerprint, recipe)`
with no hardware access — and for the same reason. A function that needs a phone in
your hand can only be tested with a phone in your hand, so in practice it is tested
once and then trusted forever.

Three consequences:

- **Every capture becomes a test case.** `01-detect.sh` writes the full descriptor to
  `bench-kit/descriptors/`, with `iSerial` stripped, and puts the filename on the
  record. Testers return that folder alongside their JSONL.
- **The whole suite runs in a second, with nothing plugged in.** `bash tests/all.sh`.
- **A tester's devices keep testing the code after they have gone.** A classifier
  change is re-run against every descriptor anyone has ever contributed.

## The suite

    bash tests/all.sh

| Check | What it catches |
|---|---|
| `tests/check-console.sh` | A syntax error in `START-HERE.html`. The console is one offline file run by someone with no console open and no way to report a stack trace; a broken edit is a blank screen at the far end of a USB stick. This check has already caught one. |
| `tests/run.sh` | The classifier disagreeing with a device whose identity a human established independently. |
| `data/merge.py --check` | Malformed records, duplicate IDs, missing consent, and IMEI/MAC-shaped strings in any field. |

## Fixtures

`tests/fixtures/*.desc` — a `lsusb -v` descriptor with optional `#!` headers:

    #!expect=adb          the class a human knows this device to be
    #!adb_state=device    what `adb get-state` said at capture time
    #!note=...            why this case exists

`#!expect` is **ground truth, not the tool's opinion.** A fixture whose expected class
came from agreeing with the scan tests nothing; it just freezes today's bug as
tomorrow's requirement. That is the same circularity `identity_source` guards against
in the matrix.

When a fixture fails, fix `classify.sh`. Change `#!expect` only if the expectation was
itself wrong, and say why in a `#!note`.

The eight fixtures shipped today are **synthetic**, hand-built to encode the two known
defects plus one trap. They are a guard against regression, not evidence of
correctness — a synthetic fixture can only encode what its author already believed. Real
descriptors from real devices are what make the suite meaningful, and they arrive from
every capture from now on.

`synthetic-cross-interface-trap.desc` is worth reading: a card reader with two
vendor-specific interfaces, `255/66/80` and `255/1/1`. Neither is ADB — the ADB triple
is `255/66/1` and needs subclass 66 and protocol 1 on the *same* interface. The obvious
`grep -A2 'bInterfaceClass 255' | grep -q 'bInterfaceProtocol 1'` matches across both
blocks and reports ADB on a card reader. That trap was written after the second defect,
by asking what *else* the same class of mistake could produce.

## The rule

Every commit that touches `classify.sh` runs `bash tests/all.sh` first. Adding a device
class or a vendor to a list means adding a fixture in the same commit. This is recorded
in `CLAUDE.md` so it survives the end of any one session.

## What this still does not catch

Honest limits, since the grant will be read by people who will ask:

- **A device nobody has.** Coverage is bounded by drawers, which is what the tester
  programme is for.
- **A wrong `#!expect`.** If a tester misidentifies their own device, the fixture
  encodes that error. `identity_source` narrows this to devices someone claimed to
  recognise; it does not eliminate it.
- **Anything past detection.** These tests cover classification, not the verifier's
  verdict logic. That needs its own golden corpus, and the false-safe gate is
  specified in `docs/verdict-contract.md`.
- **The console's behaviour, as opposed to its syntax.** A parse check is not a
  browser. Screen-by-screen testing is still by hand.
