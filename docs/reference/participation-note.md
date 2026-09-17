# Before you run anything

*Shown to every tester, above the instructions, before they plug in a device.*

---

**What this is.** A volunteer project building an open safety tool for reusing old
devices. You are helping build the reference dataset it is checked against.

**What you will do.** Plug in old devices, let the tool read them, and send back a folder.
There are two routes and you choose.

- **In your browser.** Open one file, click a button for each device, export the session.
  Nothing to install. Minutes, not hours. This route identifies and classifies a device but
  cannot read an Android phone's partition scheme or bootloader lock state.
- **From a bootable Linux stick.** Reads everything, including the Android properties the
  browser route cannot reach. Budget about 90 minutes the first time, and most of that is
  making the stick and booting it, not the work. Two to five minutes per device after that.

Either route is a real contribution. If you only have twenty minutes, take the browser.

**Nothing is written to your devices.** Every command in this protocol reads. Nothing is
flashed, erased, unlocked or modified. If a step ever asks you to flash something, it is not
this protocol and you should stop.

**What gets recorded.** What kind of device it is, its make, model and chipset, its Android
version and security patch level where that applies, its partition scheme and bootloader
lock state, which USB mode it was in, and your notes about anything awkward. Plus a handle
or your initials, whichever you prefer.

**You also send back the raw USB descriptors.** Alongside the records, the kit saves the full
`lsusb -v` output for each device into a `descriptors/` folder. These matter more than the
records: they let the classifier be re-tested against your devices long after your devices
have gone back in the drawer, so a future bug can be caught without asking you to plug
anything in again.

**`iSerial` is stripped from every descriptor at the moment of capture**, before the file is
written, because `lsusb -v` prints it and on many devices it is the hardware serial number.
A second check (`tests/check-descriptor-privacy.sh`) scans every descriptor for serials,
IMEI-shaped numbers and MAC addresses before anything is published. Two locks on the same
door.

**What is never recorded.** Serial numbers, IMEI, IMSI, MAC addresses, Android ID, ICCID,
phone numbers, or anything tied to an account. The scripts query a fixed list of properties
specifically so these cannot be picked up by accident. If you ever see one of these in
something you are about to send, delete it, and tell us, because that is a defect in the
scripts and we want to fix it.

**Your devices are yours, and the risk stays with you.** These commands read and do not
write, and the deny rules in this repository block the destructive ones outright. But
plugging old hardware into a computer is not a zero-risk act, and this project cannot take
responsibility for a device you own. If a device is precious, leave it in the drawer. A
device that will not power on or will not appear is a useful record in itself and is worth
reporting rather than forcing.

**How to send it back.** Google form link: `https://forms.gle/YkdmQvvBQMYQDKXVA`. Attach the one file you just downloaded. Its name starts with `flashguard-`. It already contains your descriptors and notes, so there is nothing else to attach. If you attach anything over 1 MB, such as a screen recording, a person looks at it before anything from it enters the published dataset. The form needs a Google account. If you do not have one, email the file to `ranaji.deb@gmail.com` instead.
Nothing else, and never a screenshot of a terminal you have not read.

**What we keep about you.** A handle or initials of your choosing, and one contact address so
we can ask a follow-up question and so you can withdraw. Nothing else. The contact address is
kept only while the project runs and is deleted when it ends; ask at any time and it is
deleted sooner. It is never published and never appears in the dataset.

**Your handle is not anonymity, and you should know that before you pick one.** The return
route is a Google Form, so submitting records the Google account you are signed in with. We
will therefore know which handle belongs to which address. That is deliberate and it exists
for one purpose: if something in a returned file looks wrong, we need to be able to come back
to the person who sent it and ask. It is not used for anything else.

**No email address of yours is published anywhere.** Not in the repository, not in the CC0
dataset, not in any log or commit, not in the published device matrix. The repository is
public and everything in it can be read by anyone, which is exactly why addresses are kept
out of it. The dataset carries your handle if you gave one, and nothing more.

**Where the data goes.** Records and descriptors are published as an open dataset under
**CC0** so other reuse and repair projects can build on them with no licence friction.

**Withdrawing.** Write to `ranaji.deb@gmail.com` and your records are removed from the dataset. No
reason needed. Records already redistributed by others cannot be recalled, which is what
publishing openly means, so it is worth knowing that before you start rather than after.

**Questions or something odd.** `ranaji.deb@gmail.com`. Awkward, confusing and broken are all useful
findings. Reporting that a step did not work is as valuable as a clean record.

---

*Placeholders in brackets are filled before this goes to anyone. `tests/check-index.sh`
fails while any remain.*
