# Schedule to 3 November

Ten weeks. Solo grant applications fail here more often than on substance: the proposal
is fine and the evidence it promised to cite was never produced in time.

Three dates are load-bearing. Everything else can slip.

| | Date | Must be true |
|---|---|---|
| **H1** | **16 September** | Public repository exists with the read-only Tier A spike. Q1 and Q2 both need a link. |
| **H2** | **14 October** | At least 10 live Android records across 3+ chipset families, both partition schemes represented. |
| **H3** | **27 October** | All seven answers drafted at final length. One week of margin, deliberately. |

---

## Week by week

**26 Aug – 2 Sep · The bench run**
Run the seven seed devices on the Acer at Tier A. Validate schema 0.2 against contact with
reality and record what had to be invented. Create the repository, private for now.
*Output: 8 to 9 records, a schema revision, a repo.*

**3 Sep · Call opens**
Read the Restack, CodeSupply and ELFA descriptions the day they appear and decide which
one this belongs in. Confirm the actual form fields against the draft and fix any
mismatch. Half a day, and it prevents the most avoidable failure available.

**3 – 16 Sep · Corpus and spike**
Import OpenAndroidInstaller's device configurations, normalise them, derive expected
verdicts. Build the read-only Tier A spike. Make the repository public. **H1.**
*This is the block that makes the validation claim defensible. Protect it.*

**8 – 21 Sep · Wave 1, three friends**
Ship `bench-kit/protocol.md`, the example record and the participation note. You are
debugging the protocol, not collecting data. Sit with one of them while they do it.
*Output: a protocol that survives someone who is not you, and a completion funnel.*

**22 Sep – 12 Oct · Wave 2, one room**
A repair café or hackerspace evening in Prague. Book it in the first week of September,
because these are scheduled well ahead and a late ask gets a November slot.
*Output: the bulk of H2, in one evening, plus a named community for Q7.*

**Late Sep – 14 Oct · Verifier and corpus**
Verdict contract to v1.0. Golden corpus running with the false-safe gate wired in. First
published coverage report. **H2.**

**7 – 27 Oct · Drafting**
Q1 and Q5 first, they carry the most weight. Q3 and Q4 need the budget decided, so decide
it early rather than discovering in week nine that it is unresolved. **H3.**

**28 Oct – 2 Nov · Margin**
Read it cold. Give it to one person who does not know the project. Cut anything that
sounds like a platform.

**3 Nov, 12:00 CET · Deadline.** Submit on 2 November. Not on the morning.

---

## What to drop if time runs short

In this order. Decide now, while it is cheap, rather than in week nine.

1. Wave 3 online recruitment. Waves 1 and 2 are enough for H2.
2. Fastboot-side reads (`03-fastboot.sh`). The adb fingerprint carries the record.
3. Corpus size beyond the first 40 or so imported recipes.

## What must not be dropped

- The public repository. Q2 is materially weaker without it.
- The false-safe gate. It is the measurable deliverable and the part of this application
  that is hardest for anyone else to write.
- Reading all three programme descriptions on 3 September.
