# Upstream projects: who to talk to, and why they would care

*Structure written 6 September 2026. THE NAMES ARE NOT FILLED IN — that needs current
research rather than recall, and a wrong maintainer name in a cold approach is worse than
no approach. This file exists so the work has somewhere to land.*

## Why this is worth doing

Impact, relevance and strategic potential are **40 percent** of the Restack score, the
heaviest weight of the three. Box 11 of the form asks for comparison with existing efforts
**and** the ecosystem engagement plan, in the same field.

A named contact — better, a letter of support — turns the strongest apparent competitor into
the strongest endorsement. Silence invites the reviewer's obvious question: *why isn't this
a patch to their project?*

Nothing else on the open-items list moves 40 percent of the score for comparable effort.

## The three projects

| Project | What they do | Why Flashguard matters to them | Contact | Status |
|---|---|---|---|---|
| **OpenAndroidInstaller** | GUI installer, 90 device configs (read 7 Sep 2026), GPL | They execute; Flashguard verifies. A pre-flight check that says "this recipe does not match this device" prevents exactly the support burden they carry. Their configs are also the corpus source. | *to research* | not started |
| **LineageOS** | Custom Android distribution, very large device coverage | Their install instructions are per-device and a mismatch bricks phones. An independent verifier reduces the bad-flash reports that reach their forums. | *to research* | not started |
| **postmarketOS** | Long-life Linux for phones, strong device-longevity framing | Closest philosophical fit — device longevity and e-waste. Most likely to care about the framing rather than only the tool. | *to research* | not started |

## What to fill in per project

- The maintainer or community manager who actually answers.
- The right channel: mailing list, Matrix/IRC, forum, issue tracker, or email. Cold email to
  a personal address is usually the worst of these.
- Whether they have a stated position on third-party tooling.
- Whether anyone has asked them something similar before, and what happened.

## How the approach should be structured

Short. Specific. Not a request for a favour.

1. **One line on what it is**, in their terms: a pre-flight check that decides whether a
   provisioning recipe is safe for a specific device, without executing it.
2. **One line on what already exists**: the device matrix, the descriptor corpus, the test
   suite, all open licensed. Concrete beats aspirational.
3. **The specific ask**, which is not "endorse us": would you use a verdict like this, and
   what would it have to get right before you would?
4. **What they get**: a CC0 device matrix and descriptor corpus they can absorb with no
   licence friction, and fewer bricked-device reports.
5. **No mention of the grant deadline as pressure.** If a letter of support comes, it comes
   because the thing is useful.

## Questions to ask, per project

These are not conversation-openers. Each one is a real blocker where the answer is theirs to
give and guessing it would be inventing a fact about someone else's project. Ask them in the
same message as the survey findings, because the findings are what earn the reply.

### OpenAndroidInstaller

**1. Is `supported_device_codes` a variant-level or a family-level claim?** The load-bearing
one, and currently the repository's only open `DISPUTED` marker.

The verifier grades variant matching: an exact variant match can reach `safe`, an unconfirmed
variant cannot. The open question is what an alias hit means. If `supported_device_codes`
lists the exact codes a recipe covers, an alias hit is as strong as an exact match and can
reach `safe`. If it names a device family, it says nothing about the variant — `hero2lte` and
`hero2ltexx` share a base code and differ in radio hardware, and a wrong flash there costs the
modem.

No test can settle it, because it is a question about what the field MEANS to the people who
maintain it. Until they answer, the verifier abstains on an unconfirmed variant regardless of
alias, which is the conservative reading and may be costing coverage on 84 of 90 devices.

*Good opening, because it is a question only they can answer and it shows the configs were
read carefully rather than scraped.*

**2. Every one of your 90 configs declares its unlock step structurally. Was that deliberate?**
The survey found 90 of 90 with an `unlock_bootloader:` step key and 90 of 90 with
`is_ab_device`. That consistency is unusual — postmarketOS declares unlock prerequisites on 0
of 556 — and it is the reason a verifier can work against their configs at all. Worth knowing
whether it is a maintained invariant or an accident, because the verifier would rely on it.

**3. Would a pre-flight verdict be useful to you, and where would it sit?** The actual ask.
Before the installer runs, not instead of it.

**4. You built a desktop application. Did the browser route fail you, or did you never try it?**
Grounded in a real result rather than curiosity. On 13 September a WebUSB probe read the
Nothing Phone 1 and the Samsung A5 identically on macOS/Brave and Windows/Edge, ADB interface
visible, no driver install. The same probe could not see a Kobo, a USB stick or a feature
phone on either platform, while both operating systems mounted them happily — Chromium
refuses whole device classes.

So a browser can classify Android phones and cannot see mass storage. If OpenAndroidInstaller
evaluated a web installer and rejected it, the reasons are worth more to this project than
anything else in this list, because they would be a year of learning for the price of a
message. If they never tried it, saying so is equally useful.

**5. Do your configs record which USB mode a device presents at each step?** The browser route
can only see some modes, so a procedure that passes through MTP or mass storage has a step the
browser cannot observe. If that is already tracked somewhere in the config, the verifier should
read it rather than infer it.

### postmarketOS

**1. Is the absence of unlock prerequisites in `deviceinfo` deliberate?** 0 of 556 declare one,
against OpenAndroidInstaller's 90 of 90. That is the clearest gap the survey found, and it may
be by design — pmaports may consider unlocking out of scope for `deviceinfo` and handle it in
the wiki instead. Ask before assuming it is an omission worth fixing.

**2. Would you accept a `deviceinfo` field for it?** Only if the answer to (1) is that it is an
omission. Do not lead with this.

### LineageOS

**1. Is the install template plus per-device metadata a stable contract, or an implementation
detail of the wiki build?** The survey recovers procedure shape from the shared template and
the `_data/devices/*.yml` records rather than from rendered pages. If that structure is
incidental, anything built on it breaks at the next wiki refactor.

**2. `custom_unlock_cmd` is set on 103 of 737 devices.** What does its absence mean on the
other 634 — no unlock needed, a standard unlock, or nobody filled it in? Absence that means
three different things is the failure this project keeps finding, and here it is in someone
else's data.

### Ask all three

**Is there already a name for "this device cannot be enumerated by a browser"?**

Before inventing a schema field for it, ask whether anyone upstream already tracks it and what
they call it. Adopting an existing term costs nothing and beats a private vocabulary that has
to be translated at every boundary.

This question exists because of a mistake made here on 13 September: fields were invented for
human variant confirmation (`variant_source`, `human_confirmed`) and an existing field with a
different meaning was read as if it carried the new one. The generalisable lesson is to ask
what a thing is called before naming it, and these three projects have between them catalogued
more device behaviour than this project ever will.

## The honest risk

They may say this should be a patch to their project rather than a separate tool. That is a
real answer and it is worth hearing before the proposal is written rather than after. The
counter, if it holds up, is that a verifier which only works inside one installer cannot be
the independent check that all three of them benefit from.
