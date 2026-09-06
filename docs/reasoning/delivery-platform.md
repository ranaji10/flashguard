# Which machine the real tool runs on

*Direction set 3 September 2026. Referenced from OPEN.md and from the tracker item
"Which machine does the real tool run on?".*

## The decision

The end user opens a **browser**. They describe what is in the drawer, pick the machine
they will run the work from (macOS, Windows, Linux), do as much as possible as a
**preliminary check in the browser itself**, and only download a package if the flow
genuinely needs one.

Testers are assumed to be mostly on Windows, some on macOS and Linux. **The bench kit is a
means to an end, not the product.** Nobody outside this project is going to make a bootable
Ubuntu stick, and asking them to is the difference between fifteen testers and three.

## Why this was reopened

It had been sitting in "deferred on purpose" under *not before the bench run*. The bench
run happened, and it exposed a problem worse than recruitment friction:

**Evidence is being collected under conditions the product will never have.** The bench kit
needs a live Ubuntu session, root, and a clean USB baseline to diff against. If Flashguard
ships as a browser tool it sees a smaller view of each device than `sudo lsusb -v` gives. A
matrix full of fields the product cannot obtain is not validation. It is a dataset about a
different tool.

## What it changes, and what it does not

**Unaffected: the USB descriptor half of the matrix.** WebUSB exposes vendor id, product id,
and every interface class, subclass and protocol — exactly the fields `classify.sh` reads.
The nine captured descriptors and the classification records built from them stay valid.

**Open: the Android half.** The seven verifier fields come from `adb`, and adb over WebUSB
means claiming the ADB interface. Chrome's documentation says the restriction is
driver-claim based and applies to *claiming*, not to reading descriptors, and that macOS,
Linux, Android and ChromeOS need no driver binding while Windows needs WinUSB. That is the
part to test rather than assume. See `docs/reasoning/webusb-findings.md` once the probe has
been run.

**Added to the schema:** `capture_route`, recording how a record was obtained — `linux-live`,
`browser`, or `package`. Without it, a record captured by a route the product will not have
cannot be told apart from one it will.

**Retired with the bench kit:** the baseline-diff trick. `01-detect.sh` identifies a device by
diffing USB against a baseline taken on a nearly empty live session. A real laptop has a
mouse, keyboard, webcam and dock attached and there is no empty baseline. Whatever replaces
it has to pick a target among many, which is a genuinely different problem and is unsolved.

## Sequence

1. **Run the probe** (`tests/webusb-probe.html`). Half an hour. It decides whether volunteers
   should be asked to boot Linux at all.
2. **Write up what it found** in `docs/reasoning/webusb-findings.md`.
3. **Build the browser tool after the verifier**, not before. Testing feasibility is an
   afternoon; building the tool is weeks, and the grant funds the verifier.

## What is still undecided

- Whether the downloadable package is per-OS binaries, a script bundle, or the current kit
  with a friendlier front end.
- Whether a "safe repurposing probability" belongs anywhere. See
  `docs/reasoning/verdict-contract.md`: Flashguard returns three values and no score. A
  probability invites a user to act on 0.8, which is the false-safe pathway the design
  exists to close. If a score is wanted for end users it is RePurpose, not Flashguard.
