# Upstream projects: who to talk to, and why they would care

*Structure written 6 September 2026. Channels and maintainers researched 13 September 2026
against the projects' own pages. Anything below that could not be confirmed says so; a wrong
maintainer name in a cold approach is worse than no approach.*

## Why this is worth doing

Impact, relevance and strategic potential are **40 percent** of the Restack score, the
heaviest weight of the three. Box 11 of the form asks for comparison with existing efforts
**and** the ecosystem engagement plan, in the same field.

A named contact, better a letter of support, turns the strongest apparent competitor into the
strongest endorsement. Silence invites the reviewer's obvious question: *why isn't this a
patch to their project?*

Nothing else on the open-items list moves 40 percent of the score for comparable effort.

## Read this before writing to postmarketOS

postmarketOS publishes an [AI policy](https://docs.postmarketos.org/policies-and-processes/development/ai-policy.html)
that forbids generative-AI-assisted contributions, and amends its
[code of conduct](https://docs.postmarketos.org/policies-and-processes/community/code-of-conduct.html)
to list using or promoting generative AI tools as unacceptable behaviour, enforceable up to a
permanent ban.

Flashguard's code has been written with AI assistance. That is a fact about this project, and
it has consequences that have to be faced rather than managed:

- **Do not offer them a patch.** A contribution would violate a policy they have stated
  plainly, and offering one anyway is not a misunderstanding, it is a decision to ignore them.
- **A question is not a contribution**, and asking one is legitimate. Write it yourself.
- **If they ask how it was built, say so.** If the honest answer means they would rather not
  engage, that is their answer and it is theirs to make. Concealing it to obtain an
  endorsement would poison the endorsement, which is the only thing the endorsement is for.
- The verifier itself is deterministic rule matching over declared fields, with no model in
  the decision path. That is worth saying because it is true and load-bearing, not as a way
  around the policy.

LineageOS takes the opposite position and [permits AI-assisted contributions](https://github.com/LineageOS/charter/blob/main/ai-coding-assistants.md)
with an `Assisted-by:` trailer, while separately banning AI-generated text in bug reports.
So there is no single disclosure answer across these three. See the `c-genai` tracker item.

## Where to send it

### LineageOS — send this one first

Actively maintained. LineageOS 23.2 shipped February 2026 and issues are being filed and
closed this month.

- **The role that exists for this:** Developer Relations Manager. The published roster at
  <https://wiki.lineageos.org/contributors> names **Kevin Haggerty (`haggertk`)**,
  **Nolen Johnson (`npjohnson`)** and **Tom Powell (`zifnab`)** in that role. `npjohnson` is
  confirmed active this quarter as the author of *Developer Verification*, 4 July 2026.
- **Where to ask:** IRC `#lineageos-dev` on Libera.Chat, web client
  <https://kiwiirc.com/nextclient/irc.libera.chat#lineageos-dev>. The Discord at
  <https://discord.com/invite/gD6DMtf> is bridged to the same channels.
- **Where NOT to ask:** the bug tracker. <https://wiki.lineageos.org/how-to/bugreport/>
  explicitly bans installation help, device-support requests and feature requests, forbids
  pinging maintainers, and forbids AI-generated report text.
- **Address the room, not a person.** Their own rules discourage pinging maintainers.
- **What they get:** their [device support requirements](https://github.com/LineageOS/charter/blob/main/device-support-requirements.md)
  mandate firmware version assertions per device. A fingerprint-versus-recipe check maps
  directly onto the thing that stops someone flashing a build against the wrong firmware
  base, and it pre-screens invalid bug reports out of a tracker their dev-rel people triage.
- **Attach to:** *Developer Verification*, <https://lineageos.org/Developer-Verification/>,
  published 4 July 2026. They have just staked a public position on independent,
  non-Google verification of what is safe to install.

### OpenAndroidInstaller — reply inside their own thread, do not email cold

**They say they are not actively maintained.** The README states it verbatim, the site repeats
it, and the last release is v0.5.5-beta from 1 July 2024. There are 383 open issues and PRs
from February 2026 still unreviewed.

**This changes something in this repository.** The open `DISPUTED` marker on
`supported_device_codes` in `flashguard/verify.py` was written as a question only they can
answer. If they cannot answer it, the conservative reading has to be adopted as a decision
with its cost stated, rather than held open indefinitely waiting for a reply.

- **Who:** **Tobias Sterbak (`tsterbak`)**, sole author and copyright holder, Berlin. Second
  and only other org member: **`MagicLike`**. Do not assume `MagicLike` speaks for the project.
- **Where:** GitHub Discussions, Q&A category —
  <https://github.com/openandroidinstaller-dev/openandroidinstaller/discussions/new?category=q-a>
- **Better than cold:** reply inside
  [Discussion #638](https://github.com/openandroidinstaller-dev/openandroidinstaller/discussions/638),
  where Sterbak returned in November 2024 and laid out four possible futures for the project,
  one of which is *creating safe, user-friendly installation instructions*. The verifier is a
  direct answer to that. Nobody volunteered on that thread and it went quiet in August 2025.
- **Email fallback:** `hello@openandroidinstaller.org`, from their README. Untested.
- **Expect weeks, or nothing.** Set that expectation before it costs a plan.
- **What they get:** a safety layer that keeps working without a maintainer, which is the
  project's actual condition, and a way to tell the ~300 unanswered *add support for X*
  requesters that no recipe matches their fingerprint instead of leaving them to try a
  neighbouring device's config.

### postmarketOS — read the section above first

Very actively maintained. Release v26.06 in June 2026, monthly updates, most recent
6 September 2026. Hosting moved to self-hosted `gitlab.postmarketos.org` in 2024.

- **Who:** the team page <https://postmarketos.org/team/> is current.
  **Stefan Hansson (`Newbyte`)** is listed for issue triage. **Pablo Correa Gómez
  (`pabloyoyoista`)** handles project coordination and grant applications and publishes
  `pabloyoyoista@postmarketos.org`. **Oliver Smith (`ollieparanoid`)**, **Clayton Craft
  (`craftyguy`)**, **Luca Weiss (`z3ntu`)** and **Casey Connolly (`kcxt`)** were all named in
  the August 2026 update, so all active within the month.
- **Where:** Matrix `#devel:postmarketos.org` for development questions,
  <https://matrix.to/#/#devel:postmarketos.org>. For device-identity questions specifically,
  `#porting:postmarketos.org`, <https://matrix.to/#/#porting:postmarketos.org>.
- **Patience is the norm.** The `#main` room topic says so in as many words: ask and wait.
- **Never** post a technical question in `#modreq:postmarketos.org`, which is for code of
  conduct reports.
- **What they get:** they already run a five-tier device categorisation — main, community,
  testing, downstream, archived — with hard promotion criteria and a demotion process. That
  is a safe / unsafe / cannot-verify judgement made by hand, by people, on a review cadence.
  Framing the verifier as tooling for a policy they already have is far stronger than framing
  it as a new product.

### One thing worth deciding before any of this

All three publish their device metadata under open licences. A working demonstration against
their real configs is a stronger opening than a question about them, and needs nobody's
permission. The reason to ask first is the `supported_device_codes` question, where guessing
would mean inventing a fact about someone else's project.

Decide, per project, whether the message is a question or a pitch. Maintainers read those very
differently and a message that is both reads as neither.

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


## Actual Questions and answers received (as of 15.09.2026)

LineageOS (asked on their Discord Server)

Q: Hello folks, bot and fellow builders, 

First of all, thanks a lot for this project. I've been rooting phones to CyanogenMOD since 2010 and the phones just work better, PERIOD. I even bought the First version of One Plus One, back when it was launched with this community's collaboration and was sad to see the partnership dissolve. And now I'm happy that it's evolved into LineageOS and that I'm talking to the people who actually built something revolutionary. Now, onto the reason why I'm reaching out - 

I'm building a tool that checks whether a recipe is safe for a specific device without executing it. Currently I have a Device Matrix built only from the devices that I have; a Descriptor Corpus that's pulled from open source device configurations, basically LineageOS, OpenAndroidInstaller and PostmarketOS; and a bunch of Verify + Test scripts to check whether it's safe / unsafe / unknown. 

My questions:
1. The installation instructions from the Wiki mentions two part structure - a) shared template b) device specific metadata files. Is this structure stable or is it something that's slated to evolve over time?

2. What does "missing unlock command" actually mean? Currently, 103 devices have 'custom_unlock_cmd' filled in, while the other 634 don't. Does it mean a) bootloader is already accessible and the device doesnt need unlocking b) uses some standard or generic unlock method c) the data is missing d) something completely different than what I can think of

3. Do you have a standard term for "device visible to OS but invisible to browser"? Are you already tracking this somewhere, if yes, could you please tell me what this schema field is called?

4. In general, would such a tool be useful to LineageOS project? Is there something the tool would need to get it absolutely nailed down before it becomes useful?

Thanks for your patience in reading through this long message. Have a great week ahead. Cheers!

A:
<irc> luk
APP
 — 11:44 AM
1. anything and everything can change on wiki over time
2. open instructions for devices you see that for and see for yourself
3. there's no such thing. we don't have completely hidden devices. the only "hiding" we do is the default filter for devices we no longer support
4. no

Q:
Thanks for your quick response. It was so quick and curt that in the first instance I thought you were an IRC bot. 

1. What I mean to ask is, can I assume that this structure will continue to exist atleast for the near future (3-5 years), and I can build my tool using these two structures as reference?
2. Thanks, I'll dig deeper.
3. Ok, understood.
4. Appreciate your honesty 

A:
not going to predict the future
tho current wiki has been jekyll based for the last ~10 years
with hundreds of device schema changes over the years

# INFERENCE
1. We should go with the assumption that the structure will stay the same
2. Run a small sub agent to do a research task that helps us decide: 
	Pick some devices that HAVE custom_unlock_cmd filled in (10 examples)
	Open their actual LineageOS installation instructions on the wiki
	Look at what unlock step they describe
	Then do the same for devices WITHOUT custom_unlock_cmd (pick a 10 different devices)
	Compare the two groups side-by-side and look for patterns. 
3. We define our own schema field, unless OAI or postmarketOS gives us an answer.
4. Doesn't change our path, we proceed as planned. 


OpenAndroidInstaller


Q: (Asked on the thread https://github.com/openandroidinstaller-dev/openandroidinstaller/discussions/638)
It's been a while since this discussion was active, and since I'm currently building something along similar lines, I thought I'll use this thread to do a temperature check.

Can the idea of eos-installer be extended further? Currently it solves for "how do I safely flash eOS with browser automation?"

I'm currently building a tool to solve the problem of "given any device and any recipe, can I verify it's safe to flash?"

Would a general verdict like that be useful? Is that something that OpenAndroidInstaller is exploring and if not, what would the tool have to get right, before it could become useful to OAI?


Q: (Asked as a new QnA Discussion thread https://github.com/openandroidinstaller-dev/openandroidinstaller/discussions/new?category=q-a)
Hello @tsterbak, @MagicLike, fellow contributors, 

First of all, thanks for putting your minds and efforts into this project and to make sure our phones can have an extended lifespan that's not dictated by manufacturers, but rather the support from an active community of like minded people.  I'll jump straight onto the reason why I'm reaching out - 

I'm building a tool that checks whether an OS build is safe for a specific device without executing it. Currently I have a Device Matrix built only from the devices that I have; a Descriptor Corpus that's pulled from open source device configurations, basically OpenAndroidInstaller, LineageOS and PostmarketOS; and a bunch of Verify + Test scripts to check whether it's safe / unsafe / unknown. I have some questions that would be helpful in making sure the tool integrates seamlessly with all of the OS builds OAI has so far, and in future.

My questions:

1. Does the 'supported_device_codes' field mean that this device build works for exactly these device codes or can it work for all devices in this family? 

2. Is your unlock-step consistency deliberate? All 90 of your configs declare unlock_bootloader: as a structural step, and declare 'is_ab_device'. Can I if enforce this as a schema requirement while building my tool?

3. Do configs record USB modes at each step? For eg, does it track that device is in fastboot -> it boots into recovery -> it mounts as MTP? 

4. Do you have a standard term for "device visible to OS but invisible to browser"? Are you already tracking this somewhere, if yes, could you please tell me what this schema field is called?

4. OAI is packaged as a desktop app. Did you try browser automation and hit some USB access or driver limits or was that never in scope?

5. Would a tool that runs at the start of the installer workflow, that lets you confidently say yes/no/unknown instead of hoping a user's device is close enough to the supported list, be useful to OAI?

Thanks for your patience in reading through this long message. Your responses would be highly appreciated and would help me decide on a direction based on the learnings from this community. Cheers and have a great week ahead! 


Q:(follow up)
Hello again, another thing came up while I was going through the configs.

I noticed a bunch of configs carry an untested: true flag. My interpretation of that is that this config was written but nobody's actually confirmed it works on real hardware yet. Is that a correct assumption?

A couple of things I'd love to know:

When that flag is set, does it mean nobody has confirmed the device works, or does it mean something like "this specific step hasn't been tested"?
When someone does confirm a device works, is the flag cleared, or is it possible that a config could have been tested but it's still showing untested: true ?
Since the direction I'm taking my tool is that it would treat any build from an untested: true config as something that should never come back as safe, but unverified. So the question is, if the flag is actually kept up to date?
Thanks in advance for your time. Cheers!



PostmarketOS

Q: (asked on https://matrix.to/#/#devel:postmarketos.org)
Hello folks and fellow builders, 

First of all, thanks for putting your minds and efforts into this project and to make sure our phones can have an extended lifespan that's not dictated by manufacturers, but rather the support from an active community of like minded people.  I'll jump straight onto the reason why I'm reaching out - 

I'm building a tool that checks whether an OS build is safe for a specific device without executing it. Currently I have a Device Matrix built only from the devices that I have; a Descriptor Corpus that's pulled from open source device configurations, basically PostmarketOS, OpenAndroidInstaller and LineageOS; and a bunch of Verify + Test scripts to check whether it's safe / unsafe / unknown. I have some questions that would be helpful in making sure the tool integrates seamlessly with all of the OS builds PmOS has so far, and in future.

My questions:

1. Is the absence of unlock prerequisites in 'deviceinfo' deliberate? I've checked 556 configs and none of them declare it. Does pmaports consider unlocking out of scope for 'deviceinfo' or is it data that hasnt been added yet? I just want to understand your architecture choice.

2. From your experience on the webflasher, do you already document which usb mode a device is in at each step? And do you have a term or schema field for "device exists but browser cant see it"?

3. Your device tier system and the promotion criteria is already a safety judgement which is being done through manual review. My verification tool is intending to automate it, such that a user gets instant feedback on whether a device fingerprint matches a build in your main tier. I'm curious as to what you think about this. 

Thanks for your patience in reading through this long message. Your responses would be highly appreciated and would help me decide on a direction based on the learnings from this community. Cheers and have a great week ahead! 