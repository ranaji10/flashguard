# NLnet open call: verified findings

*Checked 3 September 2026, 08:00–08:55 UTC, against the live pages on nlnet.nl. Two
scheduled runs fired; this file consolidates both and is the single record. The
originals are in `_superseded/` outside the repository.*

*Spot-verified by hand the same day: the generative-AI FAQ text, the AI-scope
exclusion, and the grant range. Everything else is as the runs reported it.*

---

## 1. The programme field, as it actually is

**ELFA is gone.** The ELFA page:

> **Update 2026/08:** Due to an internal reprioritisation, NLnet foundation has decided to
> withdraw from the ELFA consortium. Open calls are postponed until further notice, to be
> executed by another organisation.

No successor named, no date. Treat as closed.

**NGI Mobifree — the fund that would have fitted best — closed before we started.**
"More ethical and humane mobile software", explicitly Android-facing. Ninth and final call
ran to 1 December 2025. This is worth knowing rather than mourning: it means an
Android-provisioning safety tool was fundable at NLnet on its own terms, which is evidence
the topic is one they care about, and it can be said in the proposal.

**Open Social Fund** (ActivityPub, decentralised social) and the **Research and Higher
Education Technology Fund** are open and are not a fit. Ruled out on the record.

**The portal had not flipped yet** at 08:20 UTC — `/propose/` still said "There are currently
no calls open". The programme pages say the call opens today. Re-check before drafting into
the form.

## 2. Restack or CodeSupply

|  | **Restack** | **CodeSupply** |
|---|---|---|
| Theme | Open Internet Stack, all layers | Software supply chain security **via packaging metadata** |
| Deadline | 3 Nov 2026 12:00 CET | 3 Nov 2026 12:00 CET |
| First proposal | up to 50 k€ | up to 50 k€ |
| Per proposal max | **150 k€** | **60 k€** |
| Lifetime max per third party | **500 k€** | **60 k€** |
| Fund size | €7 M through 2030 | 1 Jun 2026 – 30 May 2029 |
| Individuals eligible | Yes, explicitly | Yes |

**Recommendation: Restack.** Its scope list is an explicit hit — "devices for
secure/privacy-friendly consumption, full stack security, reproducibility, trust-enhancing
technologies" — and Flashguard lands on four items at once. The ceiling leaves a second and
third act.

**The counter-argument, which is real.** Restack's scope is broad, so everyone applies there.
CodeSupply is narrow and unglamorous and will draw a thinner field. Flashguard *can* be framed
as supply-chain integrity: a provisioning recipe is a build artifact, and deciding safe/unsafe
without executing it is structurally the same problem as verifying a package before install.
Same first-grant size. The price is the 60 k€ lifetime ceiling — one grant, not a programme.

The tiebreaker is what Flashguard is meant to become. One-shot tool: CodeSupply is a
defensible gamble on a weaker field. Something that grows: only Restack has room.

**Third answer:** submit to Restack in November; if declined, resubmit to CodeSupply in
January or March with a supply-chain framing. Deadlines are now the 3rd of every odd month,
so a miss costs two months.

## 3. The form is two free-text boxes

The draft is organised as answers to seven questions. **The form has no such structure.**

1. Select a call · 2. Name · 3. Email · 4. Phone · 5. Organisation · 6. Country ·
7. Proposal name · 8. Website/wiki

**9. Abstract** — verbatim: *"Can you explain the whole project and its expected outcome(s).
Have you been involved with projects or organisations relevant to this project before? And if
so, can you tell us a bit about your contributions?"*

**10. Requested Amount** (Euro)

**11. Budget and context** — verbatim: *"Explain what the requested budget will be used for?
Does the project have other funding sources, both past and present? A breakdown in the main
tasks with associated effort is appreciated. Make rates explicit. (If you want, you can in
addition attach a full budget at the bottom of the form) Compare your own project with
existing or historical efforts. What are significant technical challenges you expect to solve
during the project, if any? Describe the ecosystem of the project, and how you will engage
with relevant actors and promote the outcomes?"*

12. Attachments (HTML, PDF, OpenDocument, plain text; 50 MB total) · 13. Did you use
generative AI in writing this proposal? · 14. Which model, what for · 15. Optional upload of
prompts used · 16. Privacy statement · 17. Copy to me · 18. PGP pubkey

**No word, character or page limit** anywhere — not on `/propose/`, not in either guide, not
in either FAQ. The only length guidance is about effort: the procedure is *"very light-weight"*
and *"you should be able to complete a proposal in less than an hour"*. Absence of a limit is
not licence to be long; reviewers read thousands.

Consequences:

- Box 9 must carry problem, approach, outcomes **and** track record.
- Box 11 must carry budget, rates, prior-art comparison, technical challenges **and** ecosystem
  engagement — four things in one field.
- Submissions are plain text. HTML goes in as an attachment.
- Depth belongs in attachments. Restack's second review stage asks about differentiation,
  complicating factors, claims validation, collaboration, budget justification and
  sustainability — a plain-text or PDF annex answering those pre-emptively is the right home
  for the long answers already drafted.
- Draft offline; the site recommends it to avoid losing work in the browser.

## 4. Constraints the draft does not account for

**AI-related projects are out of scope.** Verbatim from the Restack page:

> AI-related projects are not within scope — unless they are already widely used throughout
> society (> 1 million active human users) and directly relevant to the stack.

Flashguard as designed — a pure function over a fingerprint and a recipe, no model, no
training, no inference — is safely outside this. **But the vocabulary is a live hazard.** The
repository currently ships `classify.sh`, a "classifier", and a `classifier_confidence` field
carrying values like `0.85`. Every one of those is a deterministic rule over USB descriptor
fields with a hand-assigned constant, and none of it is learned from anything — but a reviewer
skimming for AI vocabulary will not know that. See §7.

**Generative-AI disclosure.** Its own section, §5.

**Payment is milestone-based, not upfront.** *"you divide your project into milestones... Once
you reach a milestone you send in a request for payment."* `grant/schedule.md` is a calendar
and must become a milestone plan with payable, externally checkable completion criteria.

**Review takes 3 to 5 months.** A 3 November submission decides somewhere in February–April
2027. Deadlines cannot be postponed; missing 3 November means 3 January 2027.

**Geographic priority.** *"Given equal proposals, inhabitants of the EU and countries
associated to Horizon Europe are given priority."* Ranaji is in Prague, so this is in his
favour and needs no special pleading. It becomes relevant only for the tester network — see §6.

**Scoring weights are published.**

| Criterion | Weight |
|---|---|
| Technical excellence and feasibility | 30 % |
| **Relevance, impact, strategic potential** | **40 %** |
| Cost effectiveness and value for money | 30 % |

Threshold to advance: total weighted score above **5.0 out of 7**. Impact carries the most
weight, so the text should spend more of its length on why an open internet stack needs this
than on how the verifier works.

**Licensing is stricter than assumed.** *"any software and hardware must be published under a
recognised open source license in its entirety"* and *"All scientific outcomes must be
published as open access."* Proprietary elements only if the open-source deliverable is
independent of them.

**Deadline, CET vs CEST.** `/propose/` says CEST; both programme pages say CET, for the same
instant. 3 November falls after the 25 October clock change, so Central Europe is on CET and
the programme pages are the internally consistent ones. Either way it is noon in Amsterdam.
**Submit a day early.** Do not plan to file at 11:55.

**Possible NixOS packaging condition — unresolved.** The Restack background page, discussing
the NixOS Foundation as consortium partner, says *"All projects within Restack use the same
state-of-the-art packaging system."* Genuinely ambiguous whether that binds funded third
parties. **Ask NLnet.** Cheap question, expensive surprise.

## 5. Generative AI: the exact wording

The Restack FAQ, asked whether generative AI may be used to write a proposal:

> The short answer is: no. Grant applications are short and we spend a lot of effort
> evaluating proposals. Please grant us the courtesy of writing the proposal yourself.
>
> If you do use generative AI to write (part of your) proposal, please put this in the text
> and explain why this was necessary.
>
> Failure to do so is likely to result in the proposal being rejected, and tarnishing your
> reputation.

Three things follow that the scheduled runs did not make explicit:

1. The disclosure is not a checkbox. It asks you to **explain why it was necessary** — a
   justification bar, not a declaration.
2. The stated objection is to *not writing it yourself*, framed as a courtesy owed to people
   who read every word. That tells you what actually offends: submitted prose that was
   generated rather than written.
3. The threatened consequence attaches to **failure to disclose**, not to use. Rejection is
   named for concealment.

Form field 15 accepts an upload of the prompts used. Keep the logs.

## 6. Questions to settle before drafting

- **Is the false-safe target gameable?** A verifier that answers `cannot-verify` for
  everything has a false-safe rate of exactly zero. A reviewer sees this in seconds. The
  headline metric needs a paired coverage metric — a stated minimum share of the corpus on
  which a definite verdict must be returned. `data/coverage.py` already reports abstain rate;
  make it a **paired gate**, not a footnote.
- **What is the false-safe rate measured against?** Zero is meaningless without labelled
  ground truth. Who adjudicates that a recipe was genuinely unsafe, and how many known-bad
  recipes exist? Technical feasibility is 30 % and this is the first question asked.
- **Who is liable when it says `safe` and a phone bricks?** A framing question, not a legal
  one. Reviewers want to see it has been thought about.
- **Has anyone spoken to OpenAndroidInstaller, LineageOS or postmarketOS?** Box 11 asks for
  comparison with existing efforts *and* the ecosystem plan. A named contact, better a letter
  of support, turns the strongest apparent competitor into the strongest endorsement. Silence
  invites "why isn't this a patch to their project?"
- **What licence do the corpora carry?** OpenAndroidInstaller's 88 configs are GPL. If the
  corpus derives from or ships with them, the choice may already be constrained.
- **Is the tester network committed?** "Tens of fingerprinted devices" depends on people who
  have signed nothing. Naming recruitment as part of the work is stronger than assuming it.
- **Where is the European dimension of the testers?** Ranaji's own residency is settled. If
  the tester network is largely in India, say so and frame it — device longevity and e-waste
  under EU right-to-repair is the obvious line, and geographic spread is a strength for
  coverage.
- **What is the tester-safety story?** Volunteers run a bench kit against their own hardware.
  A paragraph on what happens if a device is damaged, and on exactly what leaves their
  machine, pre-empts an obvious worry.
- **Ask for how much?** Cost effectiveness is 30 %. A 50 k€ ask with thin justification scores
  worse than a 32 k€ ask with explicit rates and milestones.
- **Does the 500 k€ lifetime cap follow the person or the entity?** "Per third party" is
  undefined. Matters if Flashguard later moves into a company.
- **Two applications on one deadline?** Nothing found forbids applying to both Restack and
  CodeSupply. Worth asking NLnet. The honest risk is that two thin proposals beat neither.
- **Does the NixOS packaging condition bind funded projects?** See §4.

## 7. Edits this forces

**`grant/nlnet-restack-proposal.md`** — restructure from seven answers into the two boxes plus
an annex. Lead on impact, not method. Record in one line that CodeSupply and ELFA were
considered and why they were rejected, so the decision is not re-litigated. State the licence
position in NLnet's own terms: open source *in its entirety*, outcomes open access.

**`grant/schedule.md`** — convert from calendar to milestones with payable, externally
verifiable completion criteria, each mapped to a payment request. Corpus milestones (the 88
OpenAndroidInstaller configs, LineageOS, postmarketOS) and device-fingerprint milestones are
naturally separable.

**Vocabulary sweep before the repository goes public.** Not a rename — the code names are fine
and churn costs more than it buys. Add one plain statement to `README.md` and to the proposal:
*Flashguard contains no machine learning. The classifier is a deterministic decision procedure
over USB descriptor fields; `classifier_confidence` is a constant assigned by hand to each
rule, not a model output.* Say it once, plainly, where a skimming reader will hit it.

**`data/coverage.py`** — pair the false-safe gate with a coverage floor so the primary metric
is not trivially gameable.

**`OPEN.md`** — swept the same day; see the tracker.

## Sources

https://nlnet.nl/propose/ · https://nlnet.nl/restack/ · https://nlnet.nl/restack/eligibility/ ·
https://nlnet.nl/restack/guideforapplicants · https://nlnet.nl/restack/faq/ ·
https://nlnet.nl/restack/background/ · https://nlnet.nl/codesupply/ ·
https://nlnet.nl/codesupply/eligibility/ · https://nlnet.nl/codesupply/guideforapplicants ·
https://nlnet.nl/ELFA/ · https://nlnet.nl/funding.html · https://nlnet.nl/themes/ ·
https://nlnet.nl/mobifree · https://nlnet.nl/news/2026/20260612-NGIZero-stocktaking.html ·
https://nlnet.nl/news/2026/20260803-phaseshift.html
