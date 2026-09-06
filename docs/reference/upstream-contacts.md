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
| **OpenAndroidInstaller** | GUI installer, ~88 device configs, GPL | They execute; Flashguard verifies. A pre-flight check that says "this recipe does not match this device" prevents exactly the support burden they carry. Their configs are also the corpus source. | *to research* | not started |
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

## The honest risk

They may say this should be a patch to their project rather than a separate tool. That is a
real answer and it is worth hearing before the proposal is written rather than after. The
counter, if it holds up, is that a verifier which only works inside one installer cannot be
the independent check that all three of them benefit from.
