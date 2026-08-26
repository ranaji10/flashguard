# Before you run anything

*Shown to every tester, above the instructions, before they plug in a device.*

---

**What this is.** A volunteer project building an open safety tool for reusing old
devices. You are helping build the reference dataset it is checked against.

**What you will do.** Plug in old devices, run a few commands that only read, and
send back a text file. Roughly twenty minutes for the first device and a few minutes
for each one after.

**Nothing is written to your devices.** Every command in this protocol reads. Nothing
is flashed, erased, unlocked or modified. If a step ever asks you to flash something,
it is not this protocol and you should stop.

**What gets recorded.** What kind of device it is, its make, model and chipset, its
Android version and security patch level where that applies, its partition scheme and
bootloader lock state, and your notes about anything awkward. Plus a handle or your
initials, whichever you prefer.

**What is never recorded.** Serial numbers, IMEI, IMSI, MAC addresses, Android ID,
ICCID, phone numbers, or anything tied to an account. The scripts query a fixed list
of properties specifically so these cannot be picked up by accident. If you ever see
one of these in something you are about to send, delete it, and tell us, because that
is a defect in the scripts and we want to fix it.

**Where it goes.** Records are published as an open dataset so other reuse and repair
projects can build on them. Licence: `[TO BE DECIDED: CC0 or CC-BY-SA-4.0]`.

**Withdrawing.** Write to `[CONTACT]` and your records are removed from the dataset.
No reason needed. Records already redistributed by others cannot be recalled, which is
what publishing openly means, so it is worth knowing that before you start rather than
after.

**Questions or something odd.** `[CONTACT]`. Awkward, confusing and broken are all
useful findings. Reporting that a step did not work is as valuable as a clean record.

---

*Placeholders in brackets are filled before this goes to anyone.*
