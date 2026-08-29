# Open items

Applicant: **Ranaji Deb**, sole applicant, in his own name.
Baseline swept **2026-08-29**. Critical unanswered items added **2026-08-29** in section 7b.

> **Maintained in the tracker.**
> <https://claude.ai/code/artifact/73ce736a-3f8b-4696-925c-df63ec3a9824>
> To sync: Export then Download in the tracker, drop the file here replacing this one, say "sync".

Repository: <https://github.com/ranaji10/flashguard> (private until the phones are re-captured).

Status marks: `[ ]` open · `[~]` in progress · `[x]` done · `[-]` dropped or deferred on purpose.

---

## 1. Decisions

Six of these are now settled. The reasoning is in OPEN.md and the repo, not just here.

- [x] **Project name: Flashguard, and RePurpose**
      Flashguard is the verifier, the one thing this grant funds. RePurpose is the working title for the wider ambition beyond it. Now written into both CLAUDE.md files as a scope tool: if a feature belongs to RePurpose rather than Flashguard, it is out of scope.
      **Note:** Decided. Use Flashguard for whatever is required to be built for the grant. Anything beyond, use the working title RePurpose.
- [~] **Restack, CodeSupply or ELFA** _(by 2026-09-03)_
      Cannot be decided without the pages that go live that day. A scheduled task now fires on 3 September to read all three, compare them against Flashguard, recommend one with the counter-argument, and capture the exact form fields. It runs in the cloud, so it reports back rather than editing files.
      *Blocks: the whole application*
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

- [ ] **Re-capture both phones with USB debugging ON** _(by 2026-09-07)_
      The single highest-value hour available right now. The Samsung A5 and Nothing Phone 1 were captured nine times between them and produced ZERO Android fingerprints, because USB debugging was off so 02-android.sh never ran. Without model, chipset, partition scheme and bootloader state there is nothing for a verifier to reason about. Enable debugging on both, capture again, and H2 goes from 0 live positives to 2.
      *Blocks: H2, Q1 validation claim*
      **Note:** Guide v3 now puts the USB debugging step BEFORE the phone capture rather than after.
- [x] **Deny rules verified firing at the tool level**
      Tested 26 Aug 2026, both layers independently. CLAUDE.md layer: the model refused fastboot flash citing the tiering, and also refused adb root which is NOT on the never-run list, reasoning from the design properties. settings.json layer: verified with an inert, non-device command, dd if=/dev/null of=/dev/null count=0, which returned 'Permission to use Bash ... has been denied'. Pattern-level blocking, no semantic evaluation, which is correct for a backstop. Recorded in both CLAUDE.md files.
      **Note:** Took three attempts to test properly: the documentation layer kept refusing before the permission layer got a turn. Had to pick a denied command with nothing device-related about it to isolate the mechanical rule.
- [x] **The Acer boots from USB**
      Confirmed 29 Aug 2026. Booted Ubuntu live, ran the full protocol, produced 13 records. The item flagged as blocking everything since the first review is closed.
- [x] **Camera captured, X-T30 confirmed**
      Fujifilm vendor 0x04cb, product 0x02c1, classified ptp_camera correctly. Only one USB mode captured; a second mode is still worth doing.
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
      The repository now exists with the Tier A scripts in it, so this is closer than it looks. What is left: run the bench, correct anything the run exposes, flip the repo to public.
      **Note:** Repo pushed 26 Aug (private). H1 is now gated on the bench run rather than on writing code.
- [ ] **H2: 10+ Android records, 3+ chipset families, both partition schemes** _(by 2026-10-14)_
      Chipset family is the silicon underneath: Snapdragon, MediaTek, Exynos. Partition scheme is whether the phone has two system slots that swap on update (A/B) or one (single). Ten phones on the same chipset and scheme prove far less than five spread across both. STATUS 29 Aug: 13 records, 0 fingerprints, so 0 counts toward this. Two phones are in hand and one re-capture session with debugging on moves it to 2.
      **Note:** First bench run done. The count that matters is fingerprints, not records.
- [ ] **H3: all seven answers at final length** _(by 2026-10-27)_
      One week of margin, on purpose.
- [ ] **Submit** _(by 2026-11-02)_
      Not on the morning of the 3rd. Deadline is 3 November, 12:00 CET.

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

## 7b. Critical and unanswered — added 29 Aug 2026

These came out of the second bench-run planning pass. They are here because they
are load-bearing and Ranaji has not answered them yet. Answer them in the tracker
and they move into the sections above.

- [ ] **Install node on the MacBook** — one command, `brew install node`
      Not a decision, but it belongs here because it is currently silent. Without
      node, `tests/all.sh` skips the check that catches a broken START-HERE.html
      and still reports success. On 29 Aug it skipped while a real bug
      (`declare -A`, bash 3.2) was caught only by the other checks. A suite that
      passes because a check did not run is worse than no suite.

- [ ] **How do testers return their files, and to what address?**
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

- [ ] **Are the 13 records from 29 Aug retired, or kept in the matrix?**
      *Blocks: coverage figures*
      All 13 were captured by a classifier now known to be wrong, carry no
      `identity_source`, no `device_local_id` and no saved descriptor. `coverage.py`
      already counts them as zero toward the exit criterion. Recommended: once the
      re-run lands, rename to `rana-2026-08-29.superseded.jsonl`, which keeps the file
      and the evidence while taking it out of the counts. Needs a yes.

- [ ] **Is the tester programme in the proposal, or is a solo matrix?**
      *Blocks: Q3, Q4, the schedule* — 66 days to 3 November, recruitment not started.
      A solo-built matrix plus a credible recruitment plan is defensible. A claimed
      multi-tester matrix that does not exist by submission is not.

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
- [-] **A WebUSB browser tool**
      Not before the bench run.
- [-] **A landing page or any website**
      Out of scope. That is RePurpose, not Flashguard.
- [-] **Wave 3 online recruitment**
      Only after waves 1 and 2 smooth the protocol.

## 9. Closed

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
