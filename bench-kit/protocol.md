# What's in your drawer?

*About 90 minutes the first time, then a few minutes per device. Nothing is written to your devices.*

We are building an open safety tool for reusing old phones and tablets, and we need a
reference dataset of what real devices actually report. That means old phones, but also
cameras, e-readers, USB sticks and iPhones, because half the evidence is proving the tool
does **not** mistake those for something it can flash. Nobody with a drawer is
disqualified.

**Read `participation-note.md` first.** It is short and it says what is collected, what
gets published and how to withdraw.

---

## What you need

- Any computer you can boot from a USB stick, or a Linux machine you already have
- The bench kit on a USB stick
- Whatever old devices are in the drawer, and a USB cable that carries data

## What you do

1. Boot from the Ubuntu stick, choose **Try Ubuntu**, connect to wifi.
2. Open `START-HERE.html` from the kit stick. It walks you through the rest.
3. Run `bash 00-setup.sh` once.
4. For each device: plug it in, run `bash 01-detect.sh`, fill in the record builder,
   unplug.
5. For an Android, also run `bash 02-android.sh`.
6. Download the records and send them back.

## Before you plug in an Android phone

Most of the value in a record comes from the Android properties, and none of them can be
read without USB debugging. Five minutes here saves a whole capture.

1. **Settings → About phone**, tap **Build number** seven times.
2. **Developer options → USB debugging**, on.
3. Plug in. **Look at the phone screen** — accept the authorisation prompt, tick "always allow".
4. Notification shade → USB mode → **File transfer** (not charging only).
5. **Unlock the screen and leave it unlocked** for the capture. A locked phone never shows the prompt.
6. No prompt at all? **Developer options → Revoke USB debugging authorisations**, unplug, replug.

A phone that is too old or too locked down to offer developer options should still be
captured. A device that cannot be fingerprinted read-only is itself a finding.

Nothing needs to be enabled on cameras, e-readers, USB sticks or iPhones. Plug them in as
they are.

## What we are hoping you hit

Problems. A cable that turns out to be charge-only, a device that shows up as the wrong
thing, a step whose wording made no sense at eleven at night. Those reports are worth as
much as the clean records, because making this workable for people who are not us is the
actual research question.

## What will never be asked of you

Nothing in this protocol flashes, erases, unlocks or modifies anything. If any instruction
ever tells you to run `fastboot flash`, `fastboot erase`, `fastboot oem unlock` or
`fastboot flashing unlock`, **it is not this protocol.** Stop and ask.

Serial numbers, IMEI, MAC addresses and Android IDs are never collected. The scripts read
a fixed list of properties specifically so they cannot be picked up by accident.
