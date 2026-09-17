# Index: where every decision lives

*The map from "we decided that" to "it is written here". `tests/check-index.sh` fails the
build if any path below does not exist, and fails if a file under `docs/` is missing from
this index — so a document cannot quietly become an orphan.*

**Why this exists.** On 6 September an audit found eleven things that had been decided in
conversation and written into no file at all, plus three files claiming to cover work they
predated. The tracker said the second bench run was "written up"; the write-up did not
exist. Nothing checked, so nothing caught it.

---

## Read these first

| Question | File |
|---|---|
| What are the rules of this repository? | `CLAUDE.md` |
| What is the verifier supposed to do? | `docs/reasoning/verdict-contract.md` |
| What counts as done, and what is it measured against? | `docs/reasoning/verifier-plan.md` |
| Why does it abstain where a human says unsafe? | `docs/reasoning/verdict-gap.md` |
| What is outstanding? | `OPEN.md`, generated from `docs/tracker/open-items.html` |
| Which copy of the tracker wins? | `docs/reference/sync-protocol.md` |

## Reasoning — why things are the way they are

Read before writing the proposal or changing a design.

| File | Holds |
|---|---|
| `docs/reasoning/verdict-contract.md` | The verifier specification. safe / unsafe / cannot-verify, and what each means. |
| `docs/reasoning/verifier-plan.md` | Fingerprint vs corpus vs verifier, done criteria, the paired metric, what false-safe is measured against. |
| `docs/reasoning/recipe-format.md` | The v0.1 JSON recipe shape accepted by the verifier and why it is declarative. |
| `docs/reasoning/safe-case.md` | Why v0.1 has no defensible safe case and the minimum semantic addition needed for v0.2. |
| `docs/reasoning/recipe-format-findings.md` | Five independent translations from OpenAndroidInstaller configs and the gaps they expose. |
| `docs/reasoning/recipe-format-coverage.md` | Per-project coverage of every v0.1 recipe field and source fields with no v0.1 place. |
| `docs/reasoning/prerequisite-survey.md` | Definitions and measured prerequisite, partition, and identity field counts across three upstream sources. |
| `docs/reasoning/delivery-platform.md` | Browser-first direction, what it changes about the matrix, what the bench kit stops proving. |
| `docs/reasoning/testing-protocol.md` | How defects get caught before a device is plugged in. Pure functions, fixtures, the bash 3.2 rule. |
| `docs/reasoning/prior-art.md` | OpenAndroidInstaller, LineageOS, postmarketOS. Positioning and corpus sources. |
| `docs/reasoning/verifier-readiness-review.md` | The original design review, 26 Aug. **Carries a superseded-in-parts header naming exactly which conclusions were overtaken.** Method still sound; figures and plans are not. |

## Reference — facts and procedures you look up

| File | Holds |
|---|---|
| `docs/reference/bench-hardware.md` | USB sticks, mount paths, machines, every device and its state. **Read before quoting any path.** |
| `docs/reference/participation-note.md` | What testers agree to. Canonical copy; `bench-kit/participation-note.md` must match it byte for byte. |
| `docs/reference/handoff.md` | How to hand work between VS Code and a Claude session, and how open-items provenance is tracked. |
| `docs/reference/review-workflow.md` | Every command of the review ritual in order, what each one prints, and why the reviewer is never given a summary. |
| `docs/reference/upstream-contacts.md` | Who to approach at the three upstream projects, how, and why they would care. **Names not yet researched.** |
| `docs/reference/tier-a-bench-protocol.md` | The Tier A protocol in full. |
| `docs/reference/device-test-kit.md` | Kit design notes. |
| `docs/reference/runs/bench-run-2026-08-29.md` | Run 1. The MTP/PTP defect. |
| `docs/reference/runs/bench-run-2026-08-30.md` | Run 2. First fingerprints, the controlled comparison, four defects, `cdc_modem`. |
| `docs/reference/runs/tester-attrition.md` | Devices that could not be captured, and the schema gap that exposed. |
| `docs/open-items-snapshot.md` | Copy of `OPEN.md` inside the repo. Generated. |
| `docs/reference/sync-protocol.md` | The two copies of the tracker, which one wins, and what the word "sync" means to Copilot and to a Claude session. |
| `docs/reference/review-log.md` | What each blind review found, and whether it was ever fixed. Ticked by hand only. |
| `docs/tracker/open-items.html` | **The tracker itself.** Double-click to open. Published copy lives at claude.ai; same source, two copies. |

## Grant

| File | Holds |
|---|---|
| `grant/nlnet-restack-proposal.md` | The proposal. **Still shaped for seven questions; the form has two boxes.** |
| `grant/schedule.md` | Milestones with payable, externally checkable criteria. Costing deliberately blank. |
| `docs/Research/OAI-config-analysis.md` | OpenAndroidInstaller config structure: exact-string device codes, schema-enforced `is_ab_device`, a machine-readable `untested` flag, and no checksums anywhere. |
| `docs/Research/install-method-classification.md` | All 28 LineageOS install methods classified by what the unlock requires. 303 devices are vendor-gated. Carries an analysis appendix separating verified from assumed. |
| `docs/Research/TASK-2-install-method-classification.md` | The follow-up research task: classify all 28 install methods by what the unlock requires and whether a device can ever report it. |
| `docs/Research/TASK-3-variant-danger.md` | Research task 3: where two models share a codename, does anything upstream treat them differently, and has flashing the wrong one ever cost anybody a modem? Settles the `variant` ruling. |
| `docs/Research/variant-danger-findings.md` | Task 3 result: cross-flashing across models sharing one codename blows ARB fuses, zeroes IMEIs and corrupts modem NVRAM. 89 codenames have 2-6 upstream pages each. |
| `docs/Research/variant-danger-findings.md` | Findings for research task 3: upstream model differentiation, verified damage mechanisms across vendors, evaluation of the three variant architectural options. |
| `docs/Research/reply-to-lineageos-2026-09-15.md` | What to send back to LineageOS after their answer, and the reasoning behind each line of it. |
| `docs/Research/custom_unlock_cmd-findings.md` | What absence of `custom_unlock_cmd` means in LineageOS, read from the templates. Settles it: the field is a template override, not documentation. |
| `docs/reference/producer-prompt-2026-09-14-testfix.md` | Second repair: leading whitespace zeroes every field, and two of three shape tests undo their own perturbation. Test the shipped normaliser in node. |
| `docs/reference/producer-prompt-2026-09-14-repair.md` | Repair task after the blind review: CRLF corrupting two verifier fields, a test that could not fail, pending records claiming seventeen answers. |
| `docs/reference/producer-prompt-2026-09-15-package.md` | The build task for the merged WebUSB + bench-kit tester file. Decisions already made, and where a producer will be tempted to go wrong. |
| `docs/reference/producer-prompt-2026-09-16-batch1.md` | Batch 1 of 4: the platform trap that mislabels every later record, and the pending record that claims seventeen unknowns. |
| `docs/reference/producer-prompt-2026-09-16-batch2.md` | Batch 2 of 4: the Windows command block PowerShell expands before adb sees it, and the restored bare-getprop offer guard. |
| `docs/reference/producer-prompt-2026-09-16-batch2b.md` | Batch 2b: the Windows shell split writes two `host_platform` values the schema does not define. Adds `host_shell` and a schema-agreement test. |
| `docs/reference/producer-prompt-2026-09-16-batch3.md` | Batch 3 of 4: `unlock-out-of-band` as a reason code of its own, with data-held guidance naming what a person must do by hand. |
| `docs/reference/producer-prompt-2026-09-16-batch4.md` | Batch 4 of 4: carry upstream's `untested` flag into the recipe source block and gate `safe` on it. The absent case stays undecided. |
| `docs/reference/producer-prompt-2026-09-16-batch5.md` | Batch 5: replace `variant` with a `product_model` allowlist, remove the DISPUTED marker, write the Spacewar recipe. Authorised 16 September. |
| `docs/reference/producer-prompt-2026-09-17-batch6.md` | Batch 6: fix false safe in avicii.json unlock step gating, typed upstream_untested check, bootloader_state recipe prerequisite migration. |
| `docs/reference/producer-prompt-2026-09-17-batch7.md` | Batch 7: last build before testing. Verifier final (operations require a declared unlock, declared version comparison, gate on human assessment), tester package build with checksums, session intake, testing runbook and form consent text. |
| `docs/tracker/pending-2026-09-16.md` | Pending tracker notes from 16 September. |
| `grant/work-log-2026-09-13.md` | What was actually done, 26 Aug to 13 Sep, with commits and numbers. Source material for the proposal, **not** the proposal. |
| `grant/nlnet-findings-2026-09-03.md` | The open call, verified against the live pages. Programme choice, form, scoring weights, AI rules. |
| `grant/_drafts/README.md` | Where superseded long-form answers go. Not `library/`. |

## Code and data

| File | Holds |
|---|---|
| `bench-kit/scripts/classify.sh` | The USB classifier, a pure function over descriptor text. |
| `bench-kit/scripts/derive.sh` | Android property derivation, a pure function over `key=value` text. |
| `bench-kit/scripts/01-detect.sh` | Device I/O and printing. Decides nothing. |
| `bench-kit/scripts/02-android.sh` | Allowlisted property reads over adb. |
| `bench-kit/START-HERE.html` | The tester console. |
| `data/schema.md` | The record format, v0.4. |
| `data/merge.py` | Contributions to canonical matrix. Validates, dedupes, reconciles. |
| `data/coverage.py` | Tier A scoreboard and the paired verifier gate. |
| `data/prerequisite_survey.py` | Pure text-in, record-out classifier for upstream prerequisite evidence. |
| `data/survey_upstream.py` | Filesystem runner that counts the cloned upstream sources without importing their text. |
| `data/recipe_format_coverage.py` | Reproducible measurement of v0.1 recipe-field coverage in the cloned upstream records. |
| `data/unlock_guidance.json` | Out-of-band unlock procedures and links keyed by unlock method. |
| `data/recipes/` | The corpus. Five recipes, all `cannot-verify`, none safe. |
| `tests/all.sh` | Everything checkable without a device. Run before every commit. |
| `tests/promote.py` | Descriptors to fixtures, with the ground-truth and consistency gates. |
| `tests/webusb-probe.html` | Can a browser read what Tier A needs? **Not yet run.** |
| `tests/check-index.sh` | Enforces this file: dangling paths, unindexed docs, broken editor instruction files, diverged copies. |
| `tests/check-tracker.sh` | Enforces the tracker: no dead paths, a banner that is not older than the data, and a "what changed" filter that is not silently empty. |
| `tests/handoff.sh` | Prints the handoff block. Run it before switching tools. |
| `tests/review-packet.sh` | Builds the packet for a reviewing assistant: suite, diff, and the five questions. |
| `tests/review-carry.sh` | The SECOND pass: unticked findings from earlier reviews. Never run before the blind answer is in. |
| `tests/review-log-add.sh` | Files a review into the log with the right heading, keeps the full answer, and refuses a ticked box. |
| `tests/tracker-export.py` | Regenerates `OPEN.md` and the snapshot from the tracker source. This is what "sync" runs. |
| `.githooks/pre-commit` | Runs the suite before every commit. Enable with `git config core.hooksPath .githooks`. |
| `tests/check-disputed.sh` | Collects `DISPUTED:` markers — disagreements no test can settle, needing Ranaji's ruling. |
| `tests/check-public-safe.sh` | What would become public if the repo flipped today. Tracked files only. |
| `.vscode/settings.json` | Workspace settings: Copilot review and generation rules, and the exclusions that keep `library/` out of editor tooling. |
| `.github/copilot-instructions.md` | Repo-wide rules Copilot reads automatically in every chat. Abridged from `CLAUDE.md`, which stays the source of truth. |
| `.github/copilot-review-instructions.md` | The longer review-only rules, pointed at from settings. |

## Decided and deliberately not built

| Decision | Written in |
|---|---|
| CC0 for data, GPL-3.0-or-later for code | `LICENSE`, `data/LICENSE`, `OPEN.md` |
| Restack over CodeSupply and ELFA | `grant/nlnet-findings-2026-09-03.md` §2 |
| No machine learning, and no vocabulary suggesting it | `README.md`, `CLAUDE.md` |
| Bench kit frozen until a tester is blocked | `CLAUDE.md` |
| Device owner carries the risk | `docs/reference/participation-note.md` |
| Tier C, submission endpoint, landing page: not now | `OPEN.md` §8 |

## Known gaps, on purpose

These are absent and that is recorded rather than forgotten.

- **`verify()` does not exist.** `docs/reasoning/verifier-plan.md`.
- **`data/recipes/` is empty.** Same file.
- **`DECIDED_SHARE_FLOOR` is `None`** in `data/coverage.py`, until there is a corpus to
  measure against.
- **Upstream maintainer names** in `docs/reference/upstream-contacts.md`.
- **`[CONTACT]` and `[RETURN ROUTE]`** in the participation note. `check-index.sh` fails
  while they remain, so they cannot be forgotten into a tester's hands.
- **Costing table** in `grant/schedule.md`, blank until M1 is built and can calibrate it.
