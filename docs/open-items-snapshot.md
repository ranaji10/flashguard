# Open items

Applicant: **Ranaji Deb**, sole applicant, in his own name.
Baseline swept **2026-08-29**, **2026-08-30** after the second bench run, and
**2026-09-03** after the NLnet call opened. Section 0 outranks everything below it.

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
      **Note:** Handled by the scheduled task, which fired twice. Both runs consolidated; the
      originals are in `_superseded/nlnet-2026-09-03/`.
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
      grant/nlnet-restack-proposal.md. Built from the CV variants you supplied: bioinformatics foundation, the FAMU computer-vision thesis, the CloudChef forecasting tool you actually built, 18 programmes to go-live at Cognizant, and your current agentic-AI work. The 'what I am not' paragraph is the load-bearing one; check you are willing to say it.
      *Blocks: the application*
- [ ] **Flip flashguard from private to public** _(by 2026-09-16)_
      The repo exists and holds the read-only Tier A scripts, which ARE the spike H1 asks for. What remains is confidence, not code: run the bench once so you know the scripts work on real hardware, fix whatever breaks, then flip to public in Settings. Do not recreate the repo to make it public, or you lose the history.
      *Blocks: Q1, Q2*
      **Note:** Sequence: bench run (done 29 Aug), fix what it exposed (classifier v2 and guide v3, done), re-capture the phones, then flip to public.
- [x] **Make the existing private prototype public**
      Done 26 Aug 2026. Turns 'no public contributions' into a real, if small, public record for Q2.
      **Note:** Done. Earlier repository made public on GitHub.
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
      **Note:** The A5 had debugging on during the FIRST run too. The classifier was blind
      to it, not the phone.

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
      **Note:** Gated on section 0 now, not on the bench run.
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
      **Note:** Your instinct was right and mine was over-cautious. I flagged pruning three times when the safety issue was already solved by the wall. Item closed as a deliberate decision to keep.
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


- [ ] **Generative-AI disclosure: decide the answer now** _(added 3 Sep)_
      *Blocks: submission.* The form has a mandatory field. The Restack FAQ, verbatim:
      *"The short answer is: no. Grant applications are short and we spend a lot of effort
      evaluating proposals. Please grant us the courtesy of writing the proposal yourself. If you
      do use generative AI to write (part of your) proposal, please put this in the text and
      explain why this was necessary. Failure to do so is likely to result in the proposal being
      rejected, and tarnishing your reputation."*
      Three things follow. The disclosure asks you to **explain why it was necessary** — a
      justification bar, not a checkbox. The stated objection is to *not writing it yourself*,
      framed as a courtesy owed to people who read every word. And the threatened rejection
      attaches to **failure to disclose**, not to use. Form field 15 accepts an upload of the
      prompts; keep the logs.

- [ ] **AI vocabulary sweep before the repository goes public** _(added 3 Sep)_
      Restack, verbatim: *"AI-related projects are not within scope — unless they are already
      widely used throughout society (> 1 million active human users) and directly relevant to the
      stack."* Flashguard is safely outside it. But the repository ships `classify.sh`, a
      "classifier", and a `classifier_confidence` field carrying values like `0.85` — all
      deterministic rules with hand-assigned constants, and a reviewer skimming for AI vocabulary
      will not know that. Not a rename; one plain sentence in `README.md` and the proposal.

- [ ] **The proposal is structured for a form that does not exist** _(added 3 Sep)_
      *Blocks: the proposal draft.* The draft answers seven questions. The real form is two
      free-text boxes: one carrying project, outcomes and track record; one carrying budget, rates,
      prior-art comparison, technical challenges and ecosystem engagement together. No word limit
      anywhere, but the procedure is described as "very light-weight" and completable "in less than
      an hour". Depth goes in attachments. Submissions are plain text.

- [ ] **schedule.md must become a milestone plan, not a calendar** _(added 3 Sep)_
      Payment is never upfront: *"you divide your project into milestones... Once you reach a
      milestone you send in a request for payment."* Each milestone needs a payable, externally
      checkable completion criterion.

- [ ] **Pair the false-safe gate with a coverage floor** _(added 3 Sep)_
      A verifier that answers `cannot-verify` for everything has a false-safe rate of exactly zero,
      and a reviewer sees that in seconds. Both research runs raised it independently. `coverage.py`
      already reports abstain rate — make it a paired gate with a stated minimum share of the corpus
      that must get a definite verdict. Related: zero is meaningless without labelled ground truth.

- [ ] **Talk to OpenAndroidInstaller, LineageOS or postmarketOS** _(added 3 Sep)_
      Box 11 asks for comparison with existing efforts *and* the ecosystem plan, in one field. A
      named contact — better, a letter of support — turns the strongest apparent competitor into the
      strongest endorsement. Silence invites "why isn't this a patch to their project?" Impact is
      40% of the score, the heaviest weight, and nothing moves it further for less effort.

- [ ] **Ask NLnet whether the NixOS packaging condition binds funded projects** _(added 3 Sep)_
      The Restack background page says *"All projects within Restack use the same state-of-the-art
      packaging system."* Ambiguous whether it binds third parties. Cheap question, expensive
      surprise.

- [ ] **How much to ask for** _(added 3 Sep)_
      Cost effectiveness is 30% of the score. A 50k ask with thin justification scores worse than a
      32k ask with explicit rates and milestones. Scoring: technical excellence 30%, relevance and
      impact 40%, cost effectiveness 30%; weighted total must exceed 5.0 of 7 to advance.

- [ ] **The tester-safety paragraph, and liability framing** _(added 3 Sep)_
      What happens if a volunteer's device is damaged, and exactly what leaves their machine. Most
      of the substance exists already in `docs/participation-note.md` and the descriptor privacy
      check; it needs saying in the proposal. Same for who is liable when the verifier says `safe`
      and a phone bricks — a framing question, and reviewers want to see it has been thought about.

- [ ] **Which machine does the real tool run on?** _(added 30 Aug)_
      *Blocks: whether the current matrix is valid evidence.*
      The bench kit needs an Ubuntu live USB, root, and a clean USB baseline to diff
      against. No end user will do any of that, and few testers will either. Worse:
      the matrix is being collected under conditions the product will never have, so
      fields captured now may not be obtainable by the thing being funded. Decide the
      delivery platform BEFORE collecting more data. See docs/delivery-platform.md
      when it exists.

- [ ] **Does WebUSB permit what Tier A needs?** _(added 30 Aug)_
      Cheap to answer — an afternoon. Chrome's own documentation says the restriction
      is driver-claim based and applies to *claiming* an interface, not reading
      descriptors, and that macOS, Linux, Android and ChromeOS need no driver binding
      while Windows needs WinUSB. If descriptor reading works in a browser on a normal
      laptop, the Linux-USB requirement disappears for classification. The ADB
      fingerprint needs interface claiming, which is the part to test. Do not design
      around an assumption here; test it.

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


- [ ] **How do testers return their files, and to what address?**  ← still the first blocker
      *Blocks: recruitment, participation-note.md*
      The kit assumes files come back and never says how. Attachments to a personal
      address puts that address in fifteen inboxes and their data in Gmail. Options:
      a dedicated project address, a form-and-upload service, or a repository issue
      with the file attached. Nothing else in the tester programme can start until
      this exists, because the participation note has to state it.

- [ ] **What is a tester's contact detail, legally?**
      *Blocks: recruitment*
      The device data carries no personal data by design. The channel does — a name,
      an email, a handle. Ranaji is in the EU, so that processing is GDPR-scoped, and
      testers in India bring the DPDP Act in too. Small to solve now, unpleasant after
      fifteen people have sent files. The minimum: say in the participation note what
      is kept, for how long, and how to have it deleted.

- [ ] **Does the CC0 data licence match what Ranaji expects to own?**
      *Blocks: fund choice*
      He asked whether he would "still own the full rights on how to use the insights."
      Under CC0 nobody owns the matrix exclusively, himself included, and NLnet requires
      open licensing of results. If exclusive use of the dataset was ever the plan, that
      changes which fund to apply to, not just the wording. Confirm or reject explicitly.


- [ ] **Is the tester programme in the proposal, or is a solo matrix?**
      *Blocks: Q3, Q4, the schedule* — 66 days to 3 November, recruitment not started.
      A solo-built matrix plus a credible recruitment plan is defensible. A claimed
      multi-tester matrix that does not exist by submission is not.

- [x] **Testers' answers to the closing questions are now captured** _(30 Aug)_
      They were not being captured at all — the three questions printed on a screen with
      nowhere to type. Ranaji only answered them because he opened a text editor
      unprompted; nobody else would have. There is now a box, a Save button, a leak check,
      and the answer rides out in the same file as one `record_type: "session_note"` line.
      `merge.py` collects them separately. The questions were also rewritten: they were
      written for the assistant, not for someone at midnight with a phone in one hand.

- [ ] **Who checks a returned file before it enters the matrix?**
      `merge.py --check` catches malformed records, duplicate IDs, missing consent and
      IMEI/MAC-shaped strings. It cannot catch a tester who confidently misidentifies
      their own phone, which then becomes ground truth. `identity_source` narrows this;
      it does not close it. Decide whether a second opinion is required on any record
      that becomes a test fixture.

- [ ] **Does the bench-run failure narrative go in the application?**
      Two classifier defects found, root-caused, fixed and turned into a test suite in
      one day, with the fix committed. Most applications assert methodology; this can
      show it. Ranaji's call whether it reads as rigour or as inexperience — the
      recommendation is rigour, stated plainly.

## 8. Deferred on purpose

Not problems. Decisions already made to not do these yet.

- [-] **Tier C, any real flashing**
      Not before the grant decision.
- [-] **A submission endpoint**
      Not before 20 records exist.
- [~] **A WebUSB browser tool — NO LONGER DEFERRED** _(reopened 30 Aug)_
      Moved out of "deferred" because the reason for deferring it collapsed. See section
      7b, "Which machine does the real tool run on?". This is now a decision that gates
      whether the matrix being collected is evidence at all, not a nice-to-have for later.
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
