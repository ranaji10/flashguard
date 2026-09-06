# Tier A Bench Protocol

> Guardrails, the read-only run order for the seed devices, and how the results become a tester network.
Originally published as a private web page on 26 August 2026; the operational version is `bench-kit/START-HERE.html`.

---

Guardrails to set before you plug anything in, the run order for your own seven devices on the Acer, and how the evening's results turn into a tester network.

**Writes to any device** none
**Bench time** one evening
**Output** 8 to 9 matrix records

## Guardrails, from the folder

Four things worth taking from `Resources/`, chosen because each one removes a class of error rather than making the work faster. Set these up before the bench run, not after.

Guardrail 01 from TokenSavingFrameworks / deny-noise

### Make it impossible for an assistant to flash your phone

The deny-list demo in that folder is presented as a way to stop Claude reading `node_modules` and burning tokens. Repurpose it. You will spend the next two months building this with an AI assistant that has shell access, on a desk where an Android phone is plugged in and sitting in fastboot mode. One helpful suggestion executed without a pause is a brick.

Put this in `.claude/settings.json` at your project root:

```
// .claude/settings.json
{
  "permissions": {
    "deny": [
      "Bash(fastboot flash:*)",
      "Bash(fastboot erase:*)",
      "Bash(fastboot format:*)",
      "Bash(fastboot oem:*)",
      "Bash(fastboot flashing:*)",
      "Bash(fastboot update:*)",
      "Bash(fastboot set_active:*)",
      "Bash(fastboot boot:*)",
      "Bash(adb root)",
      "Bash(adb disable-verity)",
      "Bash(dd:*)"
    ]
  }
}
```

**Verify it, do not trust it**Deny-rule syntax has changed across versions. After you write the file, ask the assistant to run `fastboot flash boot test.img` and confirm it is refused. If it is not refused, the rule is not matching and you need to fix the pattern before you keep going. A guardrail you have not tested is decoration.

**Also worth saying out loud**This protects you from the assistant. It does not protect you from yourself. The stop list in Part 2 covers that half.

Guardrail 02 from autoresearchSKILLS\_diagrams

### A golden corpus with one hard gate

That skill runs a loop: generate, evaluate against fixed criteria, keep or discard, append everything to JSONL. Strip out the diagrams and you have the shape of your regression suite, which is the single most important robustness mechanism this project will have.

Every recipe in `recipes/` carries an `expected` verdict. A runner produces actual verdicts for all of them. Results append to a log that never gets rewritten. Then one rule decides whether the run passed:

| Measure | Meaning | Rule |
| --- | --- | --- |
| false\_safe | Recipe expected unsafe, verifier said safe. A device dies. | **Must be 0. Build fails otherwise.** |
| false\_unsafe | Recipe expected safe, verifier said unsafe. Someone is inconvenienced. | Track, do not gate. |
| abstain\_rate | Share answered cannot-verify. | Report always, so a verifier that refuses everything cannot look successful. |

Your test kit already says every misclassification becomes a new case. That instinct is right and unnamed. Naming it, gating on it, and publishing the numbers is what turns a tool into evidence you can cite in Q1.

Guardrail 03 from Security For Vibe-Coded Apps

### A recipe is untrusted input, exactly like a web form

The five items in that document are written for a web app, but the mapping is close to one to one. A provisioning recipe arrives from a community contributor or a generator. It is a hostile string until proven otherwise.

- **Validate before you parse.** Schema-check every recipe against a declared format and reject on failure. Never accept a shape you have not defined.
- **Never interpolate a recipe field into a shell.** This is the document's server-side-validation point wearing different clothes, and it is the likeliest way this project ships a real vulnerability.
- **Pin your dependencies.** The hallucinated-package problem is real and you are building with an assistant.

**The architectural version of this, which matters more**Split the verifier from anything that can touch hardware. Verification should be a pure function: fingerprint in, recipe in, verdict out, no device I/O, no USB permission, no network. If the verify path structurally cannot write to a device, then "the verifier bricked my phone" stops being a bug you have to prevent and becomes a sentence that cannot be true. That is worth stating in Q6 as a design property.

Guardrail 04 from TokenSavingFrameworks / structured-specs

### Write the verdict contract before the code

The demo's point is that a specified prompt beats a vague one. The application here is narrower and more important: write down exactly what `safe`, `unsafe` and `cannot-verify` mean, and what conditions produce each, before you implement anything.

The abstain semantics are the hard intellectual problem in this project and the thing NLnet's Q6 is asking about. If you code first, the definition ends up being whatever the implementation happens to do, discovered later by reading it back. One page, written first, and the code is measured against it.

Two more from the same folder are worth ten minutes each and no more: the compressed `CLAUDE.md` demo, because your root context file should carry the scope guardrail and the stop list; and plan-at-high, execute-at-medium, because this is a months-long solo build. Ignore the other eleven, they are camera work.

## The bench run

Nothing here writes to any device. Every command reads. The order is deliberate: host first, then the six devices that must come back negative, then the one unknown Android last, when the protocol is already smooth and you are not learning two things at once.

## Phase A — Turn the Acer into the bench

45 min, once

Boot it from a Linux live USB instead of running Windows. This is not preference, it removes the worst friction in your whole protocol.

**Three reasons, and a fourth that is rhetorical**The Zadig driver dance disappears entirely, because udev rules ship working. Windows 10 has had no security updates since October 2025 and you are about to ask friends to trust this rig. Google has never committed to an end date for Chrome on Windows 10, so that path is not collapsing tomorrow, but it is on borrowed time. And the fourth: a 2012 machine whose vendor support ended, running the tool that returns abandoned devices to service, is your thesis demonstrated on your own test rig. Put that sentence in Q7.

1. From the Acer's current Windows, download a current Ubuntu LTS desktop ISO and write it to a USB stick with Rufus or balenaEtcher. Use a 16 GB or larger stick and enable persistent storage if the writer offers it, so your records survive a reboot.
2. Reboot and hold `F12` for the Acer boot menu, or `F2` for setup. On some Acer models the F12 boot menu has to be switched on in setup first. If the machine has Secure Boot, disable it there.
3. Choose *Try Ubuntu* rather than install. Connect to wifi, then install the tools:

   ```
   sudo apt update
   sudo apt install -y usbutils adb fastboot
   # if those package names are not found on your release:
   sudo apt install -y usbutils android-tools-adb android-tools-fastboot
   ```
4. Make a working directory and take the baseline with nothing plugged in. Every device reading afterwards is a diff against this.

   ```
   mkdir -p ~/bench
   lsusb > ~/bench/baseline.txt
   cat ~/bench/baseline.txt
   ```

**If you insist on staying on Windows**Chrome plus Zadig will work. One warning that matters: Zadig replaces the driver for whichever device is selected in its dropdown, and picking the wrong entry breaks that device on that machine until you roll the driver back. Only ever select the Android device while it is in fastboot mode. Log every minute of this friction, because smoothing it is a legitimate deliverable, but do not make it your default first experience.

## Phase B — The six that must come back negative

10 min each

Run these first. They carry no risk, they train your hands on the method, and they are the half of the evidence that proves your classifier does not produce false positives. For a safety tool that matters as much as the positive case.

For each device, the same three commands:

```
# 1. plug it in, then see what appeared
diff ~/bench/baseline.txt <(lsusb)

# 2. read its descriptors, using the VID:PID from the line above
sudo lsusb -v -d 04b8:0005 2>/dev/null \
  | grep -E 'bDeviceClass|bInterfaceClass|idVendor|idProduct|iProduct|iManufacturer'

# 3. write the record, then unplug before the next device
```

| Order | Expect | Watch for |
| --- | --- | --- |
| **1.** USB stick | mass\_storage | Interface class `08`. Proves the method before anything interesting is at stake. |
| **2.** External HDD | mass\_storage | Same class, different power behaviour. A second negative costs two minutes. |
| **3.** Fuji X-T30 | ptp\_camera | Interface class `06`. Then change the camera's USB mode in its menu and read it again. |
| **4.** Fuji X-T20 | ptp\_camera | Your kit writes "TX20", which is almost certainly the X-T20. Fix it in the doc. |
| **5.** Kobo | mass\_storage | May present as MTP instead depending on model and firmware. Either answer is a finding, record which. |
| **6.** iPhone 8 | ios | Apple vendor ID `05ac`. Must be flagged unsupported for flashing. Do not run identifier-listing tools on it, `lsusb` is enough to classify. |

**The Fuji two-mode case is your best early finding**The same physical camera presents as a different USB class depending on a menu setting the user made weeks ago and does not remember. That is a classifier problem with no clean solution, discovered on device three of your first evening, and it argues directly for cannot-verify as a first-class verdict. Log it as two separate records with a note linking them.

## Phase C — The unknown Android, last

30 min

Charge it above 50 percent first. A device that dies partway through a bootloader session is how avoidable damage happens, and there is no reason to be in a hurry.

1. On the phone: *Settings → About phone*, tap *Build number* seven times, then *Developer options → USB debugging* on.
2. Plug in and authorise. The first `adb devices` will say `unauthorized`; accept the RSA prompt on the phone screen, then run it again.

   ```
   adb devices
   # accept the prompt on the phone, then:
   adb devices
   ```
3. Read the fingerprint. Every property below is read-only.

   ```
   adb shell getprop | grep -E \
    'ro\.product\.(model|device|manufacturer|board)|\
   ro\.build\.(fingerprint|version\.release|version\.sdk|version\.security_patch)|\
   ro\.boot\.(slot_suffix|verifiedbootstate|flash\.locked)|\
   ro\.hardware|ro\.board\.platform|ro\.build\.ab_update'
   ```
4. Read the two fields your schema most needs:

   **Partition scheme.** A non-empty `ro.boot.slot_suffix`, typically `_a` or `_b`, means A/B. Empty or absent means single. `ro.build.ab_update` corroborates.

   **Bootloader state.** `ro.boot.flash.locked` is `1` when locked. `ro.boot.verifiedbootstate` reports `green` for locked and verified, `orange` for unlocked. Whether it is *unlockable* is a different question your schema also asks, and you will usually not be able to answer it read-only. That is a legitimate `unknown`, and noticing it is itself a finding about your schema.
5. Optional, and still read-only: look at it from the bootloader side, then bring it straight back.

   ```
   adb reboot bootloader
   fastboot devices
   fastboot getvar all 2>&1 | less
   fastboot reboot
   ```

### Stop list. Print this and tape it to the Acer.

None of these belongs anywhere in Tier A. Two of them wipe the device on contact, and the rest can leave it unbootable. There is no reason to type any of them this year.

- fastboot flashing unlock
- fastboot oem unlock
- fastboot flash …
- fastboot erase …
- fastboot format …
- fastboot update …
- fastboot set\_active …
- adb disable-verity
- dd …

**Scrub before you record, not after**Both `adb devices` and `fastboot getvar all` print the device serial number, and `getvar all` may print more. Your schema is going to be published as open data. The rule that actually holds is: never paste a raw dump into the record, copy only the named fields your schema asks for, and delete the raw output when the record is written. A regex scrub is not good enough, because an IMEI is fifteen plain digits and will slip through anything you write in a hurry. Add the exclusion list to the schema itself, where a tester will read it: never record serial, IMEI, IMSI, MAC, Android ID.

## Phase D — Write the records, then interrogate the schema

30 min

One JSONL line per device, per mode. You should finish the evening with eight or nine records: six or seven negatives, one positive, and the Acer itself as the host entry.

Then do the part that is actually research. Read back what you wrote and answer three questions in a notes file:

- **What did you have to invent?** Every field you filled with a value the schema did not anticipate is a schema defect found before you shipped it to twenty strangers.
- **What did you leave blank, and is blank distinguishable from unknown?** A camera has no `bootloader_state`. An Android whose unlockability you could not determine also has no `bootloader_state`. Those are not the same absence and your schema currently cannot tell them apart.
- **How long did each device actually take?** This is the number that determines whether a volunteer finishes. If the Android took forty minutes, your ask is not twenty minutes and you should not say it is.

**You are piloting an instrument, which you have done many times**The friend programme is data collection with a protocol, and this evening is the pilot. Treating it that way rather than as debugging gets you a second output for free: a validated instrument, which is a more defensible thing to describe in Q1 than "we tested some phones."

Sequencing

### What not to build yet

- **Do not build the WebUSB tool before this evening.** On the Linux bench everything above is four command-line tools you already have. WebUSB matters later, for the public zero-install version. Building it first means writing a classifier with no ground truth to test it against.
- **Do not build a submission endpoint until you have twenty records.** An endpoint is an attack surface with an operating cost. Until then, a file emailed to you, or a pull request, is a perfectly good transport and needs no security review.
- **Do not touch Tier C before the grant decision.** It is not required for the application and there is no version of an early brick that helps you.

## From your bench to a matrix

The bench run is what makes recruitment possible, because the thing that gets volunteers over the line is not instructions. It is a completed example they can copy.

### Ship three things, and only three

- **A protocol that fits on one screen.** If it scrolls, the completion rate drops. Your current test kit is the reference document; the tester-facing version is a quarter of its length.
- **One filled-in record, with the boring device.** Show them the USB stick entry, not the Android. It signals that ordinary junk counts, which is the whole point.
- **A participation note, above the instructions.** What is collected, what gets published, under what licence, how to withdraw. Three sentences. You write these professionally, and having it there before anyone runs anything is the difference between a project people trust and one they wonder about.

### Ask for the drawer, not for help

"Help me test flashing software" sounds like something that might break a phone. "What's in your drawer?" is a curiosity, and it is also literally accurate: Tier A writes nothing.

Make the ask precise and small. Plug in whatever old devices are in the drawer, run four commands, send back a text file, twenty minutes. Precise asks get done and vague ones get postponed, and you now know the real number from Phase D.

**The negatives are the recruiting advantage**Most volunteer hardware programmes can only use people who own the right phone. Yours needs cameras, e-readers, USB sticks and iPhones just as much, because they are the evidence of no false positives. Nobody is disqualified. Say that in the ask.

### Three waves

| Wave | Who | Purpose |
| --- | --- | --- |
| **1** | Three friends | Debug the protocol, not the tool. You are watching where they stall, not collecting data. Sit with one of them while they do it if you can. |
| **2** | One room, in person | The highest-yield idea here. A repair café or hackerspace evening in Prague puts you in a room full of old devices and people who already care about this, with you present to handle friction. Fifteen records in an evening beats any amount of online posting, and it is a specific, credible answer to the Q7 ecosystem question that is currently a TODO. |
| **3** | Communities online | Only once waves 1 and 2 have smoothed the protocol. postmarketOS and LineageOS community channels, XDA, right-to-repair groups, the Fediverse. Arrive with a published matrix and worked examples, not with a request. |

### Measure the funnel, not just the devices

Count four numbers: invited, started, completed, produced a usable record. The gap between started and completed is the protocol's real defect rate, and knowing where people drop is a finding about making device reuse accessible, which is closer to what NLnet is funding than the device data alone.

Then close the loop. Send every participant the coverage summary with their device in it. People who see their contribution in a published dataset bring the next person, and that is the only recruitment mechanism that compounds.

**What this buys you in the application**By early October you can write two sentences that most applicants cannot: a named number of devices across a named number of chipset families and both partition schemes, and a completion rate from a piloted protocol. That is the difference between promising validation and having started it.

## Referenced

- Local: `device-test-kit.md`, `Resources/TokenSavingFrameworks/deny-noise/`, `Resources/autoresearchSKILLS_diagrams/SKILL.md`, `Resources/Security For Vibe-Coded Apps (+ Prompt).md`, `Resources/TokenSavingFrameworks/structured-specs/`
- [Chrome will keep working on Windows 10, but not forever](https://www.howtogeek.com/chrome-will-keep-working-on-windows-10-but-not-forever/), on the absence of a committed end date
- Companion document: the Verifier Readiness Review, for the prior-art scan and the seven proposal changes
