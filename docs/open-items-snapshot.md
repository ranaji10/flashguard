# Open items

Applicant: **Ranaji Deb**, sole applicant, in his own name.
Baseline swept **2026-08-29**, **2026-08-30** after the second bench run, and
**2026-09-03** after the NLnet call opened. Synced from the tracker the same day, with
sixteen of Ranaji's notes answered in place. Section 0 outranks everything below it.

> **Maintained in the tracker.**
> <https://claude.ai/code/artifact/bbac4a10-81b5-49bb-b206-46e4cbe6d303>
> Find it any time at claude.ai/code/artifacts — "Verifier Open Items", shield icon.
> The banner at the top of the tracker says when it was last swept and what went in.
> To sync: Export then Download in the tracker, drop the file here replacing this one, say "sync".
>
> *Replaces <https://claude.ai/code/artifact/73ce736a-3f8b-4696-925c-df63ec3a9824> (29 Aug),
> which this session could not write to. Delete that one from the gallery so there is only
> one tracker.*

Repository: <https://github.com/ranaji10/flashguard> (private until the phones are re-captured).
Latest state: second bench run complete, classifier v4, 9 real descriptors published as test
fixtures, test suite green. **65 days to the deadline.**

Status marks: `[ ]` open · `[~]` in progress · `[x]` done · `[-]` dropped or deferred on purpose.

---

## 0. The next thing, which is not any of the things below

Added 30 August 2026 after counting what is actually in the repository.

- [ ] **Write the verifier** _(by 2026-09-08)_
      *Blocks: the grant. Everything else in this file is downstream of it.*

      The repository is **6,430 lines and none of them are the verifier.** There is no
      `verify(fingerprint, recipe) -> safe | unsafe | cannot-verify`. `data/recipes/`
      contains a README and nothing else, so there is no corpus. The false-safe rate —
      the primary metric, the build gate, the centre of the proposal — has no subject
      to measure. Everything built so far is instrumentation for collecting the inputs
      to a function nobody has written.

          tests/       2,126 lines
          bench-kit/   1,832
          docs/        1,414
          data/          683
          grant/         375   <- untouched since 26 August

      This is drift, and most of it is the assistant's. Improving the bench kit gives
      fast feedback: a test goes green, a bug is found, numbers move. Writing the
      verifier means an unsolved problem with no scaffolding. Every individual
      improvement was defensible, which is exactly how a project ends up with excellent
      instrumentation and no deliverable.

      **What "done" means for a first version:** a pure function matching
      `docs/verdict-contract.md`; ten recipes in `data/recipes/`, five safe and five
      deliberately unsafe; the false-safe gate wired into `tests/all.sh` and failing the
      build on a single false safe; abstain rate reported alongside. Roughly 200-300
      lines. Tier A being incomplete does not block this: the verifier takes a
      fingerprint as input, and there is now one real complete fingerprint plus a schema,
      which is enough to write against.

- [x] **Freeze the bench kit** _(30 Aug)_
      It works. It produced a complete seven-field record. `CLAUDE.md` now carries the
      rule: no bench-kit change unless a tester is blocked, and when asked what to do
      next, the answer is the verifier until one exists. That rule binds the assistant
      more than it binds Ranaji.

- [ ] **Smaller turns**
      Six defects shipped in roughly 24 hours — `grep -m1`, `grep -A2`, the partition
      inference, `declare -A`, a broken JavaScript string, and identity loss in
      `sameDeviceAgain`. The suite catches them now, but the rate is the signal. Four
      hundred lines in one turn is not reviewable, and review is the only defence.
      Push back when it happens.

## 1. Decisions

Six of these are now settled. The reasoning is in OPEN.md and the repo, not just here.

- [x] **Project name: Flashguard, and RePurpose**
      Flashguard is the verifier, the one thing this grant funds. RePurpose is the working title for the wider ambition beyond it. Now written into both CLAUDE.md files as a scope tool: if a feature belongs to RePurpose rather than Flashguard, it is out of scope.
      **Note:** Decided. Use Flashguard for whatever is required to be built for the grant. Anything beyond, use the working title RePurpose.
- [x] **Programme: Restack** _(settled 2026-09-03)_
      ELFA is dead — NLnet withdrew from the consortium in August 2026, no successor named. NGI
      Mobifree, which would have fitted best (ethical mobile software, explicitly Android-facing),
      closed its final call in December 2025. That leaves Restack and CodeSupply. Restack's scope
      names devices, full-stack security, reproducibility and trust-enhancing technologies —
      Flashguard hits four at once — and its ceilings are 150k per proposal and 500k lifetime
      against CodeSupply's 60k and 60k.
      The real counter-argument is competition, not scope: Restack is broad so everyone applies
      there, CodeSupply is narrow and will draw a thinner field, and Flashguard *could* be framed
      as supply-chain integrity. The price is a 60k lifetime ceiling — one grant, not a programme.
      Fallback if declined: resubmit to CodeSupply on 3 January or 3 March with that framing.
      Full findings: `grant/nlnet-findings-2026-09-03.md`.
      originals are in `_superseded/nlnet-2026-09-03/`.
      **Note:** Handled by the scheduled task. Nothing to do until 3 September.
- [x] **Code licence: GPL-3.0-or-later**
      Chosen with eyes open. It is NOT free of limitations: copyleft means anyone distributing a modified version must publish their source. That is the right constraint here, because a safety verifier whose checks can be quietly weakened in a closed fork is worth less. It also keeps OpenAndroidInstaller's GPL material usable as a corpus source. Revisit only if you later want commercial products to embed the verifier privately, which would argue for Apache-2.0.
      **Note:** Decided on your instruction to take the recommendation, with the trade-off stated rather than hidden.
- [x] **Data licence: CC0 for data/**
      The matrix and recipe corpus go out under CC0 so postmarketOS, LineageOS, OpenAndroidInstaller and anyone else can absorb them with no friction. Share-alike protects little on a factual dataset and blocks exactly the adoption that is the Q7 argument.
      **Note:** You asked for clarity rather than a choice. This is the reasoning; say so if you disagree.
- [x] **Contact address: an email for testers**
      It only ever meant one email address in the participation note, so a tester can send records, ask when something breaks, and withdraw their data. Nothing to do with where testers are located.
      **Note:** Question answered. Still needs an actual address filled into docs/participation-note.md.
- [ ] **Requested amount and person-months**
      EUR 20k to 40k is plausible. NLnet pays per completed milestone on request, never upfront, so the figure has to break into milestones you can evidence one at a time.
      *Blocks: Q3, Q4*

## 2. Applicant status

Settled: Ranaji Deb, sole applicant, in his own name. NLnet states anyone may apply, individuals included, and pays individuals directly.

- [x] **UNDP outside-activity question: not applicable**
      The UNDP contract is Anna's. Ranaji is the applicant and has no active employment contract, so nothing restricts the application. This was flagged as blocking everything. It is closed.
      **Note:** The UNDP contract is on my wife's (Anna) name. The grant application will be filed by me (Ranaji Deb).
- [x] **IP clauses: not applicable**
      No employment contract to claim IP in what you build.
      **Note:** I currently don't have any active employment contracts.
- [ ] **Czech tax treatment of the grant**
      NLnet grants are donations from a Dutch public benefit organisation, paid per completed milestone on request. NLnet says taxation varies by country and to ask your local authority. The narrow question for an accountant: is a milestone-based donation from a Dutch ANBI to a private individual treated as a gift or as income here, and does receiving it need a zivnostensky list? Not legal or tax advice. Ask before the first milestone is claimed, not before applying.
      **Note:** Researched as far as credible sources allow. The rest genuinely needs a Czech accountant.

## 3. Q2 and the public record

Q2 was rebuilt from your CVs on 26 August. It was previously written around Anna's evaluation career, which was my error.

- [ ] **Read the new Q2 draft and make it yours**
      The Q2 material is NOT obsolete — the second half of box 9 is the same question: “Have you
      been involved with projects or organisations relevant to this project before?” So it
      survives, compressed from a long answer to a paragraph. Source is grant/nlnet-restack-
      proposal.md, built from the CV variants: bioinformatics foundation, the FAMU computer-vision
      thesis, the CloudChef forecasting tool, 18 programmes to go-live at Cognizant, the current
      agentic-AI work. WHAT REMAINS: read it and decide you are willing to say it, particularly
      the 'what I am not' paragraph.
      *Blocks: the application*
      *Moved: 2026-09-03*
      **Note:** Is this still relevant now, considering the grant form only has box 9 and 11? — 3
      Sep: Yes, but as source material rather than as a deliverable. The second half of box 9 IS
      the Q2 question — “have you been involved with projects or organisations relevant to this
      project before?” So the content survives, compressed to a paragraph. The 'what I am not'
      line is exactly the kind of thing that belongs there.
- [ ] **Flip flashguard from private to public** _(by 2026-09-16)_
      The repo exists and holds the read-only Tier A scripts, which ARE the spike H1 asks for. What remains is confidence, not code: run the bench once so you know the scripts work on real hardware, fix whatever breaks, then flip to public in Settings. Do not recreate the repo to make it public, or you lose the history.
      *Blocks: Q1, Q2*
      **Note:** Should I link my Github to Claude now? I'm a little wary of that, since the last website project code that I was working on broke after I added Github. — 30 Aug: Sequence: bench run (done 29 Aug), fix what it exposed (classifier v2 and guide v3, done), re-capture the phones, then flip to public.
- [x] **Make the existing private prototype public**
      Done 26 Aug 2026. Turns 'no public contributions' into a real, if small, public record for Q2.
      **Note:** I have made my earlier repository on github as public. — 30 Aug: Done. Earlier repository made public on GitHub.
- [ ] **Finish Certified in Cybersecurity (ISC2)**
      Listed as in progress on your CV. For a safety-tooling grant this is a genuine asset and belongs in Q2. If it will not be done by early October, leave it out of the answer rather than describing it as pending.
- [ ] **Q4: budget lines as claimable milestones**
      NLnet pays per milestone, so the budget and the milestone plan are the same document.
- [ ] **Q7: named communities and Prague groups**
      Two objectives, not one. First, recruiting testers, because the matrix needs devices you do not own. Second, Q7 asks how results reach an ecosystem, and named communities you have a real route into answer that far better than a list of famous project names.
      **Note:** What is the objective of reaching out to forums and Prague groups? Recruiting testers, and answering Q7 credibly.

## 4. Drafts to read critically

- [ ] **docs/participation-note.md**
      The withdrawal clause especially. Also needs the contact address filled in.
- [ ] **docs/verdict-contract.md**
      The intellectual core, with four unresolved design questions at the end.
- [ ] **grant/nlnet-restack-proposal.md, Q1**
      Check the two-corpus validation claim is one you are willing to be held to.
- [ ] **data/schema.md**
      Designed from reasoning, not from contact with devices. The bench run tests it.

## 5. Verify before relying on

- [x] **Re-capture both phones with USB debugging ON**
      Done 29-30 Aug. Both phones fingerprinted. **Nothing Phone 1 is the first complete
      record in the matrix**: QTI SM7325, Android 15, virtual_A/B from
      `ro.virtual_ab.enabled=true`, bootloader locked from `ro.boot.flash.locked=1`,
      verified boot green — all seven fields, each with its evidence recorded beside it.
      Samsung A5 gave five of seven: it exposes no partition and no bootloader property
      at all, and the record says so with `"absent is not the same as single"` rather
      than guessing. That is the abstain case, from real hardware.
      to it, not the phone.
      **Note:** Guide v3 now puts the USB debugging step BEFORE the phone capture rather than after. — 30 Aug: The A5 had debugging on during the FIRST run too. The classifier was blind to it, not the phone.

- [x] **The classifier defect is fixed and measured** _(30 Aug)_
      Classifier v4. Reads every USB interface rather than the first, detects the ADB and
      fastboot triples anywhere in the descriptor, and treats `adb get-state` as decisive.
      **The A5 is a controlled before-and-after**: same phone, same debugging state, same
      cable, same machine, v2 said `ptp_camera`, v4 says `adb`. One variable moved. That
      single comparison is the strongest evidence in the dataset and belongs in the
      proposal.

- [x] **A test suite exists that runs with no device attached** _(30 Aug)_
      `bash tests/all.sh` — portability (bash 3.2), console parse, console logic,
      classifier fixtures, Android derivation, descriptor privacy, data validation.
      Classification and Android derivation are now pure functions over text
      (`classify.sh`, `derive.sh`), the same shape the verifier must have. It has already
      caught four of the assistant's own defects, one of them within minutes of the code
      first touching a Mac.

- [x] **Nine real USB descriptors published as fixtures** _(30 Aug)_
      Captured with `iSerial` stripped, verified clean line by line, committed and pushed.
      Six carry human ground truth via `tests/promote.py`; three are kept as evidence but
      refused as assertions. **An abstention cannot be ground truth** — marking `unknown`
      "correct" means "I agree you cannot tell", not "unknown is what this is", and
      promoting it would lock the classifier out of ever improving on that device. The
      guard is automatic.

- [x] **A device class nobody had thought of** _(30 Aug)_
      The old Samsung turned out to expose a CDC AT-command modem — a pre-Android
      handset. The classifier had no case for USB class `0x02` and abstained. There is
      now a `cdc_modem` class, and the phone is its test. None of the eight synthetic
      fixtures contained a class their author did not already know existed. This is the
      argument for real descriptors, in one device.
- [x] **Deny rules verified firing at the tool level**
      Tested 26 Aug 2026, both layers independently. CLAUDE.md layer: the model refused fastboot flash citing the tiering, and also refused adb root which is NOT on the never-run list, reasoning from the design properties. settings.json layer: verified with an inert, non-device command, dd if=/dev/null of=/dev/null count=0, which returned 'Permission to use Bash ... has been denied'. Pattern-level blocking, no semantic evaluation, which is correct for a backstop. Recorded in both CLAUDE.md files.
      **Note:** Took three attempts to test properly: the documentation layer kept refusing before the permission layer got a turn. Had to pick a denied command with nothing device-related about it to isolate the mechanical rule.
- [x] **The Acer boots from USB**
      Confirmed 29 Aug 2026. Booted Ubuntu live, ran the full protocol, produced 13 records. The item flagged as blocking everything since the first review is closed.
      **Note:** I want to move to this one now. I've added the Repurpose folder to Claudecode on the macbook app. What exact steps should I follow?
- [x] **Cameras captured; X-T30 is dead**
      Fuji X30 (0x04cb:0x02c1) classified `ptp_camera` correctly and is now a fixture.
      The X-T30 will not power on after charging — recorded as a finding, not a gap: a
      share of any volunteer's drawer will not boot, and the proposal makes a feasibility
      claim about recruiting drawers.
      **Note:** The X-T20 came back `not_detected` while visibly taking charge (green
      light), on a cable proven good on other devices. That is a distinct condition from
      "no cable" and the schema currently has no way to say it. See section 7b.
- [ ] **Re-confirm the prior-art figures before submitting**
      88 devices, 523 stars, 380 issues were read on 26 August. All of them move.

## 6. Dated

- [ ] **Book a repair cafe or hackerspace evening in Prague** _(by 2026-09-07)_
      Booked well ahead; a late ask gets a November slot, after the deadline.
      *Blocks: H2*
- [x] **Pushed to a private GitHub repo**
      Done 26 Aug 2026. github.com/ranaji10/flashguard, private, commit 5856219, 30 files. Author is Ranaji Deb via the GitHub noreply address, so no personal email is in the history. GPL-3.0-or-later LICENSE, CC0 on data/, SPDX headers on the scripts, LF line endings pinned. The project no longer exists only on one laptop.
      **Note:** Backup and version history now real. Push authenticated with a fine-grained token scoped to this repo only.
- [ ] **H1: public repository with the read-only Tier A spike** _(by 2026-09-16)_
      The bench run is done and the defects it exposed are fixed, so the Tier A half of
      this is real. What is left: decide whether "spike" includes a first `verify()` —
      it should, or H1 demonstrates a device scanner rather than a verifier — then flip
      the repo public.
      **Note:** At what point should I start pushing this to my own Github? — 30 Aug: Gated on section 0 now, not on the bench run.
- [ ] **H2: 10+ Android records, 3+ chipset families, both partition schemes** _(by 2026-10-14)_
      `python3 data/coverage.py` scores this every time it runs. **STATUS 30 Aug:**

          [ ] android records with all seven fields   1 of 10
          [ ] distinct chipset families among them    1 of 3
          [x] non-android classified correctly        6 of 6
          [x] false safes (must be zero)              0 of 0

      The arithmetic this yields: roughly **eight more Android phones, mostly post-2018**,
      because older hardware tends to expose no partition or bootloader property. That is
      a recruitment target with a number behind it rather than a feeling, and it is the
      concrete argument for the tester programme in the proposal.
      *At risk:* recruitment has not started and 65 days remain.
      **Note:** So these are the various parameters of devices that I should test and show in my proposal? — 30 Aug: The count that matters is complete fingerprints, not records.
- [ ] **H3: all seven answers at final length** _(by 2026-10-27)_
      One week of margin, on purpose.
- [ ] **Submit** _(by 2026-11-02)_
      Deadline 3 November 2026, noon Amsterdam. The programme pages say CET and `/propose/` says
      CEST for the same instant; 3 November falls after the 25 October clock change, so CET is the
      consistent reading. Submit a day early — do not plan to file at 11:55. Deadlines cannot be
      postponed and now fall on the 3rd of every odd month, so a miss costs two months. Review
      takes 3 to 5 months, so a November submission decides around February to April 2027.

## 7. Raised and passed over

- [x] **Classifier could not tell a phone from a camera. Fixed.**
      The finding of the first bench run, and it belongs in Q6. USB interface class 0x06 covers both PTP (cameras) and MTP (phones in file-transfer mode). v1 mapped 0x06 straight to ptp_camera, so two real Android phones in nine USB modes were all recorded as cameras and coverage.py reported 0 live positives from a session that physically contained two. This is the /e/OS codename problem in a different costume and strictly worse: that one produced a harmless false negative, this one hands a verifier the wrong device class, which is a false-safe pathway. v2 resolves 0x06 by interface string then vendor ID; replayed against the 13 records it corrects all nine and leaves the four correct ones alone. Written up in docs/bench-run-2026-08-29.md.
      **Note:** Exactly what a bench run is for. Worth citing in Q6 next to the hero2ltexx case.
- [ ] **Deny rules cannot see inside script files**
      Found while verifying the guardrails. Deny rules inspect the command Claude types, not what that command then reads. 'bash script.sh' is matched as 'bash script.sh'; a destructive line inside the script is invisible to the permission layer. Environment runners like docker exec and npx are not unwrapped either. This gap is live for this project because the bench kit runs as 'bash 01-detect.sh'. Mitigation is procedural, not technical: read what a script contains before running it, and keep the printed stop list on the wall.
      **Note:** No fix available at the permission layer. Worth knowing rather than worth solving.
- [x] **pxpipe: real tool, specifically wrong for this project**
      github.com/teamchong/pxpipe is MIT, 6.7k stars, actively maintained, and genuinely clever: it renders bulky text context as PNG images because image tokens are priced by pixel area rather than content, cutting bills by 59-70%. The catch is in its own documentation: it is LOSSY, and it warns about silent misreadings of exact strings such as hex identifiers. This project is made almost entirely of exact strings: USB IDs like 0x04cb:0x02d5, build fingerprints, slot suffixes, and device codenames where hero2ltexx versus hero2lte is the difference between a correct verdict and a wrong one. Using pxpipe here would introduce precisely the class of error the verifier exists to prevent. Worth knowing about for other work. Not for Flashguard.
      **Note:** You asked whether pxpipe would be useful. Checked properly rather than guessed: good tool, wrong project.
- [ ] **How to derive expected verdicts from OpenAndroidInstaller configs**
      The largest unsolved technical question in the plan, and the Q1 validation claim depends on it. A concrete first test now exists: take ten of their device configs, hand-label the expected verdict for each by reading the config against a device the matrix knows, and see whether you can do it consistently from the config alone. If a human cannot, no verifier will. One evening, and it should happen before H1.
      *Blocks: Q1 credibility*
      **Note:** How can I test this? The ten-config hand-labelling experiment above.
- [x] **Keep library/ as it is. Decision, not a chore.**
      Reversing my earlier advice. The real risk was ever letting borrowed, differently-licensed material into a libre-licensed repo, and the project/ vs library/ wall closed that completely. What is left is 338 MB of disk, which is not a problem. Keeping it means exactly what you asked: anything in there can be referenced later if it turns out to matter. Expect that to be rare. I searched every text file in library/ for phone, bootloader, firmware, flashing, WebUSB, LineageOS, postmarketOS and adb, and got zero hits. Treat it as your general reference shelf, not as feedstock for Flashguard.
      **Note:** I havent pruned it yet, since I'm not sure if the library might be useful again at a later point. — 30 Aug: Your instinct was right and mine was over-cautious. I flagged pruning three times when the safety issue was already solved by the wall. Item closed as a deliberate decision to keep.
- [-] **Whether library/ should leave the folder entirely**
      Moot now that keeping library/ is a decision rather than a pending chore. It stays where it is.
- [ ] **Tier C written consent instrument**
      Deferred twice, no owner, no date. Fine while Tier C is off the table. Stops being fine the moment anyone suggests a real flash.
- [x] **Timing claim corrected from measurement**
      Was a guess. Measured: about 90 minutes end to end the first time including making sticks and booting, then 2 to 5 minutes per device (median 2). protocol.md and the guide now say so.

## 7b. Critical and unanswered — opened 29 Aug, swept 30 Aug

Load-bearing questions Ranaji has not answered yet. Answer them in the tracker and
they move into the sections above. Items marked `[x]` here were answered on 30 August
and are kept in place, rather than moved to section 9, because the reasoning is what
matters and it is easier to find beside the question that prompted it.

**Twelve still open. The first three are ordered; the rest are not.**

- [ ] **THE BIG ONE: the verifier does not exist** — see **section 0**, at the
      top of this file, which is where it now lives and what it now outranks.


- [~] **Generative-AI disclosure: decide the answer now**
      DECIDED 3 Sep: the compliance route. Ranaji writes the proposal himself; the disclosure is
      narrow and truthful. Mechanically it goes in FIELD 13 (yes/no) and FIELD 14 (the
      explanation), not box 9 or 11, with field 15 available for prompt logs; the FAQ's “put this
      in the text” makes one plain line in box 9 the belt-and-braces reading. WHAT REMAINS: the
      exact wording of field 14, and it must not say the technical work was “entirely authored by”
      an AI — that is inaccurate and it hands a reviewer a reason to doubt feasibility, which is
      30 percent of the score. Accurate version: tooling written with AI assistance under Ranaji's
      direction and review; design decisions, safety properties and proposal text his.
      *Blocks: submission*
      *Moved: 2026-09-03*
      **Note:** I'll follow the compliance route. Write the proposal myself and disclose that the
      technical aspects of the project was entirely authored by you, while the idea maturation was
      done by the back and forth between our conversation. Practically does this mean box 9 and
      11? Or is it part of the attachment package? — 3 Sep: Field 13 and 14, not box 9 or 11.
      Field 13 is the yes/no, field 14 is where the explanation goes, field 15 accepts the prompt
      files. The FAQ also says “put this in the text”, so one plain line inside box 9 is the belt-
      and-braces reading. ONE CORRECTION to your wording, and it matters. Do not write that the
      technical aspects were “entirely authored by” an AI. It is not accurate — you specified the
      design, made every judgement call, caught what the tooling got wrong, and rejected several
      of my recommendations — and it hands a reviewer a reason to doubt you can do the funded
      work, which is 30 percent of the score. The accurate version: the bench tooling was written
      with AI assistance under your direction and review; the design decisions, the safety
      properties and the proposal text are yours.

- [ ] **AI vocabulary sweep before the repository goes public**
      CONFIRMED 3 Sep as worth doing, and it is a DOCUMENTATION change rather than a code change,
      so it blocks nothing and must not delay the verifier. Restack, verbatim: “AI-related
      projects are not within scope — unless they are already widely used throughout society (> 1
      million active human users).” Flashguard is outside it, but the repo ships classify.sh, a
      “classifier”, and classifier_confidence values like 0.85 — all deterministic rules with
      hand-assigned constants. WHAT REMAINS: one sentence in README.md and in the proposal, done
      next time README is open and in any case before the repo flips public on 16 September.
      *Moved: 2026-09-03*
      **Note:** does it mean doing the sweep now makes sense before we do any more code or
      architectural changes? — 3 Sep: Yes, and it costs about ten minutes — but it is a
      documentation change, not a code change, so it blocks nothing and must not delay the
      verifier. Do it whenever README.md is next open, and definitely before the repo flips public
      on 16 September.

- [~] **The proposal is structured for a form that does not exist**
      DECIDED 3 Sep: restructure into what the form actually is. Box 9 carries project, outcomes
      and track record. Box 11 carries budget, rates, prior-art comparison, technical challenges
      and ecosystem plan together. The long answers already written are not wasted — synthesise
      their essence into an attachment, keeping the parts that strengthen the case. ARCHIVE
      DESTINATION: grant/_drafts/ or _superseded/, NOT library/, which holds borrowed differently-
      licensed material behind the licensing wall. WHAT REMAINS: the restructure itself.
      *Blocks: the proposal draft*
      *Moved: 2026-09-03*
      **Note:** can we restructure the proposal for the actual one that we will be submitting? The
      ideal way to treat the answers to the questions that dont exist, would be to synthesize
      their essence and see which parts make our case stronger as attachments. The rest can be
      archived somewhere in the Library folder. — 3 Sep: Yes, and the synthesis approach is right.
      One correction on where the rest goes: NOT library/. That folder is borrowed, differently-
      licensed third-party material behind the licensing wall, and putting your own drafts in it
      breaks the one rule that folder exists to enforce. Archive to grant/_drafts/ inside the
      repo, or to _superseded/ beside the NLnet runs.

- [ ] **schedule.md must become a milestone plan, not a calendar**
      Three things that are easy to conflate, separated 3 Sep. FINGERPRINT: what the bench kit
      produces — model, chipset, partition scheme, bootloader state for a real device. These are
      the INPUTS. CORPUS: a set of provisioning recipes with human-established verdicts, drawn
      from OpenAndroidInstaller's 88 device configs and the LineageOS and postmarketOS install
      instructions. This is what the verifier is MEASURED AGAINST, and it does not exist.
      VERIFIER: the function between them. Milestone shape once the verifier exists: M1 verifier
      plus corpus v1 with the false-safe gate running; M2 device matrix to N devices with the
      tester programme; M3 browser-side detection; M4 release, documentation and upstream
      handover. WHAT REMAINS: write it, after the verifier. Blocked by section 0.
      *Moved: 2026-09-03*
      **Note:** so if i understand this correctly, the device fingerprint milestone is the
      verifier that we are working on now? I'm not sure what the corpus milestone means and how it
      is related to openandroid installer, lineage or postmaker. Are we already in a position to
      have a milestone structure in place? — 3 Sep: No — the fingerprint and the verifier are
      different things, and that confusion is worth clearing up before the budget is written.
      DEVICE FINGERPRINT = what the bench kit produces. Model, chipset, partition scheme,
      bootloader state for a real device. These are the INPUTS. CORPUS = a set of provisioning
      recipes with known-correct verdicts. OpenAndroidInstaller ships 88 device configs; LineageOS
      and postmarketOS publish install instructions per device. Each is a recipe, and for each you
      need a human-established answer to 'is this safe for this device'. That labelled set is what
      the verifier is measured against, and it is the thing that does not exist yet. VERIFIER =
      the function that takes a fingerprint and a recipe and returns safe / unsafe / cannot-
      verify. Are we ready for a milestone structure? Once the verifier exists, yes — and the
      natural shape is roughly: M1 verifier plus corpus v1 with the false-safe gate running; M2
      device matrix to N devices with the tester programme; M3 browser-side detection; M4 release,
      documentation and upstream handover.

- [ ] **Pair the false-safe gate with a coverage floor**
      MECHANISM SETTLED 3 Sep: two numbers in coverage.py rather than one, and the build fails if
      either is missed. (1) false_safe == 0. (2) decided_share >= X, the proportion of corpus
      recipes given a definite safe or unsafe rather than cannot-verify. X gets picked once the
      corpus exists and there is something real to measure — naming a number before then is a
      guess. Both are then stated in the proposal AS A PAIR, so 'zero false safes' can never be
      read as 'it refuses everything'. WHAT REMAINS: the corpus. Blocked by section 0.
      *Moved: 2026-09-03*
      **Note:** how exactly can we achieve this? — 3 Sep: Concretely: two numbers in coverage.py
      instead of one, and the build fails if EITHER is missed. (1) false_safe == 0. (2)
      decided_share >= X, where decided_share is the proportion of corpus recipes that got a
      definite safe or unsafe rather than cannot-verify. Pick X once the corpus exists and there
      is something real to measure — proposing a number before then is a guess. Then state both in
      the proposal as a pair, so 'zero false safes' can never be read as 'it refuses everything'.

- [ ] **Talk to OpenAndroidInstaller, LineageOS or postmarketOS**
      Impact is 40 percent of the score, the heaviest weight, and nothing moves it further for
      less effort: a named contact — better, a letter of support — turns the strongest apparent
      competitor into the strongest endorsement. Box 11 asks for comparison with existing efforts
      AND the ecosystem plan in one field, so silence invites “why isn't this a patch to their
      project?”. WHAT REMAINS, and Ranaji has asked for it: current maintainer names for
      OpenAndroidInstaller, LineageOS and postmarketOS, the right channel for each, how to
      structure the approach, and what each project gains. Needs current research rather than
      recall — its own turn.
      *Moved: 2026-09-03*
      **Note:** can you help me pull out the relevant people in all three organization who would
      be best person to discuss this with? How should the reach-out be structured? what would be
      their benefit out of endorsing the project? — 3 Sep: Worth doing properly rather than from
      memory — it needs current maintainer names, the right channel for each project, and what
      each one actually gains. Its own turn.

- [ ] **Ask NLnet whether the NixOS packaging condition binds funded projects**
      THE QUESTION TO ASK, in one line: “Does the requirement that Restack projects use a common
      packaging system apply to funded third parties, and if so, is a Nix package expected as a
      deliverable?” IF YES: one extra milestone, packaging Flashguard as a Nix derivation — for a
      small shell-and-Python tool with almost no dependencies, probably one to two days, so a
      budget line rather than a problem, though it constrains later distribution. IF NO: nothing
      changes. WHERE TO ASK: NLnet run a monthly office hour, which can also settle the AI-
      assisted-code question and whether one applicant may submit to both Restack and CodeSupply.
      *Moved: 2026-09-03*
      **Note:** can you elaborate on this? what exactly should I be asking and what does it mean
      for the project overall? — 3 Sep: WHAT TO ASK, in one line: “Does the requirement that
      Restack projects use a common packaging system apply to funded third parties, and if so, is
      a Nix package expected as a deliverable?” WHAT IT MEANS IF YES: one extra milestone —
      packaging Flashguard as a Nix derivation. For a small shell-and-Python tool with almost no
      dependencies that is genuinely small, probably one to two days, and it is a budget line
      rather than a problem. It would also constrain how the tool is distributed later. WHAT IT
      MEANS IF NO: nothing changes. Either way it is better known than guessed, and their monthly
      office hour is the place to ask.

- [ ] **How much to ask for**
      The visibility gap is smaller than it feels: NLnet grants are almost entirely TIME. There is
      no infrastructure cost here — the verifier is a pure function, the console a static file, no
      server and no hosting bill. So the budget is hours times a rate, plus a small line for
      devices and travel. METHOD: list the milestones, estimate days per milestone honestly, pick
      a defensible rate, multiply, show the arithmetic. Cost effectiveness is 30 percent of the
      score and what is scored is whether the number is JUSTIFIED, not whether it is low — a 32k
      ask with visible arithmetic beats a 50k round number. WHAT REMAINS: the milestones have to
      exist first. Blocked by the milestone item.
      *Moved: 2026-09-03*
      **Note:** I'm unsure about this. I don't have full visibility on the infrastructure costs
      and the cost of my time or any other future costs that might arise during building this and
      after it goes live. — 3 Sep: That visibility gap is smaller than it looks, because NLnet
      grants are almost entirely YOUR TIME. Infrastructure here is close to zero: the verifier is
      a pure function, the console is a static file, there is no server and no hosting bill. So
      the budget is hours times a rate, plus a small line for devices and travel. A way to derive
      it: list the milestones, estimate days per milestone honestly, pick a defensible hourly or
      daily rate, multiply, and show the arithmetic. Cost effectiveness is 30 percent of the score
      and the thing being scored is whether the number is JUSTIFIED, not whether it is low. A 32k
      ask with visible arithmetic beats a 50k round number.

- [ ] **Who is liable when it says safe and a phone bricks?**
      POSITION RECORDED 3 Sep: the device owner is liable; the tool's job is to report honestly
      what it found. That is consistent with the participation note and it is the right answer.
      UNRESOLVED, and it needs deciding before the text is written: the second half of that
      position — that the tool should give “the probability of a safe repurposing” — describes a
      DIFFERENT PRODUCT. Flashguard returns safe / unsafe / cannot-verify, three values and no
      probability, and the discipline is that it abstains rather than scores. A probability
      invites someone to act on 0.8, which is the false-safe pathway the design exists to close.
      If a score for end users is wanted, it belongs in RePurpose. DECIDE WHICH ONE IS BEING
      PROPOSED.
      *Moved: 2026-09-03*
      **Note:** the person owning the device should be liable if the phone is bricked. The tool
      should accurately capture the probability of a safe repurposing / booting based on what we
      find on the device and what insights the device matrix brings. — 3 Sep: Your position on
      ownership is the right one and it is what the participation note already implies. But there
      is a real tension in the second half worth catching now: “probability of a safe repurposing”
      is a DIFFERENT PRODUCT from what the proposal describes. Flashguard as specified returns
      safe / unsafe / cannot-verify — three values, no probability — and the whole discipline is
      that it abstains rather than scores when it cannot be sure. A probability invites a user to
      act on 0.8, which is exactly the false-safe pathway the design exists to close. If you want
      a score for the end user, it belongs in RePurpose, not Flashguard. Decide which one you are
      proposing before the text is written.

- [ ] **The tester-safety paragraph, and liability framing**
      APPROVED 3 Sep: include it. A short paragraph on what happens if a volunteer's device is
      damaged, and on exactly what leaves their machine. Most of the substance already exists —
      docs/participation-note.md, the allowlisted property reads, iSerial stripped at capture,
      tests/check-descriptor-privacy.sh before publication. This is writing, not building. WHAT
      REMAINS: draft the paragraph when the proposal is restructured.
      *Moved: 2026-09-03*
      **Note:** yes please add it.

- [~] **Which machine does the real tool run on?**
      DIRECTION SET 3 Sep. The end user opens a browser, describes what is in the drawer, picks
      the machine they will run it from, does preliminary checks in the browser itself, and only
      downloads a package if the flow needs one. Testers are assumed to be mostly on Windows, some
      on Mac and Linux. The bench kit is a means to an end, not the product. WHAT THIS CHANGES:
      the USB descriptor half of the matrix stays valid, because WebUSB exposes vendor id, product
      id and every interface class — exactly what classify.sh reads. The Android half is the open
      question, since the seven verifier fields come from adb and adb over WebUSB means claiming
      an interface. It also ADDS a schema field recording how a record was captured — Linux live,
      browser, or downloaded package — so records obtained by a route the product will not have
      can be told apart. WHAT REMAINS: the WebUSB test settles the rest.
      *Blocks: whether the current matrix is valid evidence*
      *Moved: 2026-09-03*
      **Note:** Benchkit, is the means to an end. We can assume that the testers would mostly be
      on a windows machine. But yes, they could also be on a mac or linux. the final version of
      the tool that an end user will see, would need to be available on all platforms. Ideally,
      the end user opens a browser, enters some brief details about what devices are in the drawer
      that needs repurposing, selects which main device (mac/windows/linux) will be used as a base
      to run the tests required to safely repurpose the device, and the appropriate package can be
      provided according to the selection. It would also be great if the user can do some
      preliminary checks (like getting a safe probability of repurpose score) from the browser
      itself. This what they dont have to download anything on their system unnecessarily. Does
      this context change the may the matrix is structured currently? — 3 Sep: This is a clear
      direction and it changes the plan more than it changes the matrix. What it does NOT change:
      the USB descriptor half. WebUSB exposes vendor id, product id, and every interface class,
      subclass and protocol — exactly the fields classify.sh reads. Those records stay valid. What
      it MIGHT change: the Android half. The seven verifier fields come from adb, and adb over
      WebUSB means claiming the ADB interface. Whether that works on each platform is the thing to
      test. What it ADDS to the schema: a field recording HOW a record was captured — Linux live,
      browser, or a downloaded package — so a record obtained by a route the product will not have
      can be told apart from one it will.

- [ ] **Does WebUSB permit what Tier A needs?**
      THE TEST, half an hour: a single HTML file with one button calling
      navigator.usb.requestDevice({filters:[]}), printing device.configuration.interfaces —
      vendor, product, and every interface class, subclass and protocol. Open it in Chrome on the
      Mac, plug in the two phones and the Kobo, compare against the nine descriptors already
      captured. Matching interface classes prove browser-side classification. HOW FAR WITHOUT
      INSTALLING ANYTHING, as far as can be established without testing: identification and
      classification are descriptor reads and very likely browser-only everywhere; the Android
      fingerprint needs interface claiming, which Chrome's documentation says works driver-free on
      macOS, Linux, Android and ChromeOS but needs WinUSB binding on Windows — so Windows is the
      one that may need a download. Do not design around that summary; the test is cheap. DO IT
      THIS WEEK: it decides whether volunteers should be asked to boot Linux at all.
      *Moved: 2026-09-03*
      **Note:** how exactly can i test this? What i'm interested in knowing is, how far can a user
      go into the entire flow, without having to install anything on their laptop or computer? — 3
      Sep: HOW TO TEST: a single HTML file with one button calling
      navigator.usb.requestDevice({filters:[]}), then printing device.configuration.interfaces —
      vendor, product, and every interface class. Open it in Chrome on the Mac, plug in the two
      phones and the Kobo, and compare what it prints against the nine descriptors already
      captured. If the interface classes match, browser-side classification is proven. Half an
      hour. HOW FAR WITHOUT INSTALLING ANYTHING, as far as can be established without testing:
      identifying the device and classifying it — very likely browser-only on every platform,
      since that is descriptor reading. The Android fingerprint needs interface claiming, which
      Chrome's documentation says works without a driver on macOS, Linux, Android and ChromeOS but
      needs WinUSB binding on Windows — so Windows is the one that may need a download. Actual
      flashing over WebUSB is possible in principle. The honest answer is that the boundary is
      testable in an afternoon and should not be assumed from my summary.

- [ ] **Multi-device: the baseline-diff trick does not survive to the product**
      The kit identifies a device by diffing USB against a baseline taken on an empty
      live session. A real laptop has a mouse, keyboard, webcam and dock attached and
      there is no empty baseline. Whatever replaces it must pick a target among many.

- [x] **Install node on the MacBook** _(done 30 Aug)_
      `tests/all.sh` now runs the console parse check and the console logic tests instead
      of silently skipping them. The skip message is loud now if it ever happens again.

- [x] **Are the 13 records from the first run retired?** _(answered 30 Aug: yes)_
      `data/contributions/rana-2026-08-29.superseded.jsonl` — kept on disk, reported by
      `merge.py`, not merged, not counted. `merge.py` skips any `*.superseded.jsonl`. The
      file stays because the before-and-after comparison is evidence.

- [x] **Old Samsung: one phone or two?** _(answered 30 Aug: one, in two modes)_
      `0x04e8:0x6845` (CDC modem + mass storage) and `0x04e8:0x675a` (mass storage only)
      are the same physical handset. Both fixtures say so.

- [x] **Should testers return their descriptors?** _(answered 30 Aug: yes)_
      No grant downside; the opposite — a CC0 corpus of real USB descriptors is more
      durable than the matrix it produced, and NLnet's model is reusable open output.
      **Still to do before asking anyone:** say it in `docs/participation-note.md`, say
      that `iSerial` is stripped at capture, and say that
      `tests/check-descriptor-privacy.sh` runs before publication. Right now a tester
      would be sending a folder nobody told them about.

- [x] **Multiple devices plugged in at once?** _(answered 30 Aug: no, but test the refusal)_
      `01-detect.sh` refuses outright, and should: `adb get-state` errors with two Android
      devices attached, attribution stops being certain, and bus power gets unreliable.
      The gain is minutes; the cost is the one property the matrix rests on. **Worth
      thirty seconds of deliberate testing** — plug in two things and confirm the refusal
      message reads sensibly to someone who is not Ranaji. A tester WILL leave a mouse
      plugged in.

- [ ] **The schema cannot express "powered but invisible"**
      The Fuji X-T20 drew charge (green light) on a cable proven good elsewhere and still
      came back `not_detected`. That is a different finding from "no cable" or "dead
      device", and there is nowhere to say it. This is a live instance of the "what did
      you have to invent" question, found by the person who wrote the question.

- [ ] **`ro.board.platform` is not reliably the chipset**
      The A5 reports `exynos5` there while `ro.hardware` says `samsungexynos7580` — and
      the 7580 is not an Exynos 5 part. On a Pixel the reverse holds. Neither ordering is
      universally right. Generic values are now skipped and every candidate is kept on the
      record as `chipset_candidates`, so the choice can be redone against more devices
      without recapturing anyone's drawer. Revisit once the matrix has more silicon in it.


- [~] **How do testers return their files, and to what address?**
      DIRECTION SET 3 Sep: files go to shared cloud storage, with the kit eventually pushing them
      in one click at the end of a session. TWO THINGS THAT COME WITH THE ONE-CLICK VERSION: an
      OAuth dependency inside the kit, which is more to break on a stranger's machine, and
      testers' files landing in a personal Drive, which makes Ranaji the data controller for
      whatever is in them. A shared upload folder link needs no code and no account and is a fine
      wave-1 answer; the one-click push earns its complexity at wave 3. WHAT REMAINS: pick the
      wave-1 destination and write it into docs/participation-note.md, which is what unblocks
      recruitment.
      *Blocks: recruitment, and docs/participation-note.md*
      *Moved: 2026-09-03*
      **Note:** Ideally it should all be uploaded to a google or one drive. We can decide on the
      exact execution of this later. Off the top of mind, the kit can push the files to a linked
      drive with one click at the end. — 3 Sep: Workable, and the one-click push is the right end
      state. Two things it brings that are worth knowing before choosing it: an OAuth dependency
      in the kit, which is more to break on a stranger's machine, and their files landing in your
      personal Drive, which makes you the data controller for whatever is in them. A shared upload
      folder link needs no code and no account and is a fine wave-1 answer; the one-click push
      earns its complexity at wave 3.

- [ ] **What is a tester's contact detail, legally?**
      *Blocks: recruitment*
      The device data carries no personal data by design. The channel does — a name,
      an email, a handle. Ranaji is in the EU, so that processing is GDPR-scoped, and
      testers in India bring the DPDP Act in too. Small to solve now, unpleasant after
      fifteen people have sent files. The minimum: say in the participation note what
      is kept, for how long, and how to have it deleted.

- [x] **Does the CC0 data licence match what Ranaji expects to own?**
      CONFIRMED 3 Sep: CC0 stands, open licensing is the direction. Nobody owns the matrix
      exclusively, Ranaji included, and that is the intent rather than a cost. It also matches
      what NLnet requires of results, so no tension remains between the licence and the fund.
      *Blocks: fund choice*
      *Moved: 2026-09-03*
      **Note:** Yeah, that's confirmed. Open licensing is the way forward. — 3 Sep: Closed. CC0
      stands.


- [x] **Is the tester programme in the proposal, or is a solo matrix?**
      CONFIRMED 3 Sep: the tester programme is real and planning assumes it. Ranaji is confident
      of recruiting. The proposal can therefore describe a multi-tester matrix as the plan rather
      than hedging to a solo build — with the recruitment work named as part of the funded effort,
      not as an assumption. The coverage arithmetic stands: roughly eight more Android phones,
      mostly post-2018.
      *Blocks: Q3, Q4, the schedule*
      *Moved: 2026-09-03*
      **Note:** I'm confident of getting testers. So please count on that while doing any
      planning. — 3 Sep: Closed. Planning assumes the tester programme is real.

- [x] **Testers' answers to the closing questions are now captured** _(30 Aug)_
      They were not being captured at all — the three questions printed on a screen with
      nowhere to type. Ranaji only answered them because he opened a text editor
      unprompted; nobody else would have. There is now a box, a Save button, a leak check,
      and the answer rides out in the same file as one `record_type: "session_note"` line.
      `merge.py` collects them separately. The questions were also rewritten: they were
      written for the assistant, not for someone at midnight with a phone in one hand.

- [ ] **Who checks a returned file before it enters the matrix?**
      SHARPENED 3 Sep by Ranaji's challenge that the check belongs at the tool's end. It largely
      does. AUTOMATIC: verify the descriptor actually contains what the claimed class requires —
      an ADB triple for adb, mass storage for mass_storage, a CDC modem for cdc_modem. That
      catches any mislabel the evidence contradicts, and it belongs in tests/promote.py as a gate
      before a descriptor is promoted to an assertion. NOT AUTOMATABLE: a tester who says “Samsung
      A5” about an A3 — the descriptor is consistent either way. But the fixtures do not assert
      model names, they assert the CLASS, so this is a limitation to state in the docs rather than
      a process to build. No physical second opinion is needed. WHAT REMAINS: write the
      consistency gate.
      *Moved: 2026-09-03*
      **Note:** Shouldn't the check be done at your end? What kind of second opinion are you
      talking about? You mean physically have someone verify whether the tester identifying the
      phone is correct or not? — 3 Sep: Fair challenge, and it makes the answer better. I CAN
      check consistency automatically: does the descriptor actually contain what the claimed class
      requires — an ADB triple for adb, mass storage for mass_storage, a CDC modem for cdc_modem?
      That catches a tester who mislabels in a way the evidence contradicts, and it belongs in
      tests/promote.py as a gate before any descriptor is promoted to an assertion. What I CANNOT
      check is a tester who says “Samsung A5” about a phone that is really an A3 — the descriptor
      would be consistent either way. That was what 'second opinion' meant, and no, it does not
      mean a physical inspection. The proportionate answer is that model names are not what the
      fixtures assert; they assert the CLASS. So the automatic consistency check closes the part
      that matters, and the rest can stay an accepted limitation stated in the docs.

- [x] **Does the bench-run failure narrative go in the application?**
      CONFIRMED 3 Sep: it goes in, stated as rigour. Two classifier defects found, root-caused,
      fixed and turned into a test suite, with commits to show it, plus a controlled before-and-
      after on one phone. Most applications assert methodology; this shows it. Belongs in box 11
      next to the technical-challenges question.
      *Moved: 2026-09-03*
      **Note:** yes, please go with rigor. — 3 Sep: Closed. The failure narrative goes in, stated
      as rigour.

## 8. Deferred on purpose

Not problems. Decisions already made to not do these yet.

- [-] **Tier C, any real flashing**
      Not before the grant decision.
- [-] **A submission endpoint**
      Not before 20 records exist.
- [~] **A WebUSB browser tool — NO LONGER DEFERRED**
      AGREED 3 Sep to start, with one distinction that matters for the days remaining. TESTING
      whether WebUSB reads what Tier A needs is an afternoon, it de-risks the matrix, and it
      happens now. BUILDING a WebUSB tool is weeks and is not what the grant funds — the grant
      funds the verifier. SEQUENCE: run the test this week, let it settle the platform question,
      keep the build behind the verifier.
      *Moved: 2026-09-03*
      **Note:** Let's start on this. — 3 Sep: Agreed, with one distinction that matters for the 61
      days left. TESTING whether WebUSB can read what Tier A needs is an afternoon, it de-risks
      the matrix, and it should happen now. BUILDING a WebUSB tool is weeks and it is not what the
      grant funds — the grant funds the verifier. Recommend: run the test this week, let it settle
      the platform question, and keep the build behind the verifier.
- [-] **A landing page or any website**
      Out of scope. That is RePurpose, not Flashguard.
- [-] **Wave 3 online recruitment**
      Only after waves 1 and 2 smooth the protocol.

## 9. Closed

- [x] **Second bench run, 29-30 Aug 2026**
      10 records, 8 physical devices, first Android fingerprints, first complete record,
      9 real descriptors, one new device class, four assistant defects caught by the suite.
      Written up in `docs/bench-run-2026-08-29.md` and `docs/testing-protocol.md`.
- [x] **The Acer now dual-boots Ubuntu**
      No longer dependent on the live USB for the bench machine. Does not change the
      question in 7b about what the *product* runs on — if anything it sharpens it, since
      the bench conditions have moved further from the end user's, not closer.

- [x] **The web documents are now in the repository**
      26 Aug 2026. The readiness review and bench protocol are in project/docs/ as markdown, so the prior-art reasoning and design rationale no longer live only behind links.
- [x] **Q2 rebuilt from the correct applicant's background**
      26 Aug 2026. The previous draft was written around Anna's evaluation career. Rebuilt from Ranaji's CVs.
- [x] **Folder split into project/ and library/**
      26 Aug 2026.
- [x] **OpenAndroidInstaller added as prior art**
      26 Aug 2026. Q5 comparison, Q1 positioning, corpus source, Q7 first consumer.
- [x] **All seven readiness-review changes applied**
      26 Aug 2026.
- [x] **Git repository initialised in project/**
      26 Aug 2026. Staged, not committed: set git user.name and user.email, then commit.
- [x] **Scheduled task created for 3 September**
      26 Aug 2026. Compares all three programmes and captures the form fields.
