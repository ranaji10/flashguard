# Review log

*What each blind review found, and whether it was ever fixed.*

**Why this exists.** `tests/review-packet.sh` hands a reviewer a diff and nothing else, so
that it reads the work rather than the producer's account of it. That blindness is right
for finding defects and useless for tracking them: every review began and ended in the
same session, and a finding nobody acted on simply vanished. This file is the memory the
reviewer is deliberately denied.

**How to use it.** Five commands, two pastes, and nothing to retype.

1. `bash tests/review-packet.sh | pbcopy` — paste into a fresh session as the first
   and only message. No summary, no context. Let it answer.
2. Copy its whole answer. It ends with a paste-ready block, because the packet asks for
   one — filing a review must not mean reading five paragraphs and hand-writing
   checkboxes from them, or it becomes the step that gets skipped.
3. `pbpaste | bash tests/review-log-add.sh "short label"` — files it here with the
   right heading and today's date, keeps the full answer in a collapsed block, and
   refuses a ticked box.
4. `bash tests/review-carry.sh | pbcopy` — paste into the **same** session as a second
   pass, and it says which earlier findings are fixed, still true, or no longer meaningful.
5. Tick by hand, then commit. Only a person ticks a box.

**The rule that keeps this honest.** A finding that survives three reviews has stopped
being a finding and become a decision. Move it into the tracker and tick it here with a
note saying where it went. A log full of ancient open boxes is a log nobody reads.

**A finding is not a verdict.** Reviewers invent concerns when they cannot find real ones.
Record a finding only when the review cited a line. If it made a claim with nothing
traceable behind it, that is worth noting as a failed review rather than as a finding.

---

## Format

Written by `tests/review-log-add.sh`, so this is what it produces rather than what anyone
has to remember:

    ## 2026-09-06 — 250698b — verdict gap write-up
    - [ ] `flashguard/verify.py:151` coverage reports safe_case_available without a
          reader ever being told what would change it
    - [x] `tests/all.sh:12` soft failure aggregated but exit code not propagated
          — fixed in 141a6f1

Each entry keeps the reviewer's whole answer underneath in a collapsed block, so "was this
actually reviewed" stays answerable. `review-carry.sh` skips fenced blocks, so a finding
quoted inside the stored answer is not counted a second time.

---

<!-- NEWEST REVIEW DIRECTLY BELOW -->

## 2026-09-17 — uncommitted-on-a0713b1 — Batch 6 task

- [ ] flashguard/verify.py:308 _is_unlock_prerequisite introduces undocumented string-matching
      heuristics ("unlock" in declared_by.lower()) to guess if a step is an unlock, masking the absence
      of a formal schema marker and providing a path to a false safe
- [ ] tests/test_verify_v2.py:554 a completely unasked-for RecipePrerequisitesProduceableTest
      was added that analyzes shell scripts and markdown with regex, out of scope for the PR
- [ ] flashguard/verify.py:517 the source.untested fallback is retained as a "deprecated
      fallback" indefinitely with no end date and no writer, exactly as criticized previously
- [ ] data/recipes-v0.2/a5xelte.json:1 the recipe retains a nine-model allowlist while citing
      an upstream config that contains no model strings, leaving its provenance unrecorded
- [ ] tests/test_verify_v2.py:249 the test named for omitting unlock_class still manually
      re-inserts "unlock_step": True, ensuring it passes by supplying the marker it claims to omit
- [ ] tests/test_verify_contract.py:52 test_model_mismatch_is_unsafe_not_abstention still uses
      GD1YQ (which is in the allowlist), passing due to a device mismatch instead of testing models
- [ ] docs/reasoning/verdict-contract.md:123 the specification still formally defines the
      variant field and the safety tiers built on it, although the verifier no longer reads it
- [ ] docs/reasoning/recipe-format-coverage.md:53 the measurement record still tabulates
      target.variant and assets.variant, which no longer exist in the working corpus
- [ ] data/recipe_format_coverage.py:60 the postmarketos row is still matched against
      ^deviceinfo_models=, a key that exists nowhere in the upstream device files
- [ ] flashguard/verify.py:385 product_model is incorrectly appended to fields_consumed before
      validation, falsely asserting the field was verified on execution paths lacking a model list

<details><summary>the review, as it came back</summary>

```
1. What changed that was not asked for?
   The diff replaces the unasked-for is_unlock_step alias by building a new, unasked-for set of implicit text-matching heuristics in _is_unlock_prerequisite (e.g., checking if declared_by contains "unlock", or matching against hardcoded key names). It also introduces a completely unrequested RecipePrerequisitesProduceableTest that statically scans bash scripts and regexes markdown tables to validate prerequisites.
2. What did it decide that was not already in a file?
   The heuristic matching in _is_unlock_prerequisite unilaterally decides whether a prerequisite qualifies as an unlock step by string-guessing rather than enforcing an explicit schema marker. It decided to indefinitely keep the source.untested fallback with no sunset date and exactly zero processes that write it, precisely as criticized in the previous review. Finally, it decides to keep the nine-model hardware footprint for a5xelte.json based entirely on an upstream file containing no model names, leaving the hardware scope undocumented.
3. Does any test pass for a reason other than the code being correct?
   Yes, two tests. test_renamed_unlock_prerequisite_omitted_unlock_class_abstains is designed to test what happens when the unlock class is omitted, yet it illegitimately inserts "unlock_step": True into the test recipe; it passes because the test actively supplies the trigger rather than demonstrating that omissions are safely evaluated. Additionally, test_model_mismatch_is_unsafe_not_abstention continues using GD1YQ—a model explicitly permitted in the SAFE_RECIPE allowlist—alongside a wrong product_device, meaning the test succeeds strictly due to a device mismatch instead of the model mismatch it claims to exercise.
4. Does any file, name or comment describe something as existing that does not?
   Yes, several:
- docs/reasoning/verdict-contract.md:123 still actively defines the variant field and the safety tiers built strictly upon it, despite the verifier no longer parsing such a field.
- docs/reasoning/recipe-format-coverage.md:53 continues to tabulate target.variant and assets.variant measurements across the corpus, though those fields have been eliminated.
- data/recipe_format_coverage.py:60 still attempts to match the regex ^deviceinfo_models=, which exists absolutely nowhere in the upstream postmarketos sources.
- flashguard/verify.py:385 unconditionally claims product_model was consumed as evidence, creating an evidence stamp that describes the field as safely evaluated even on code paths where no models list exists and the verification aborts early.

5. Does anything here create a path to a false safe?
   Yes. The text-guessing codebase heuristics in _is_unlock_prerequisite introduce a 0-day path to a false safe. Because the schema no longer has an enforced generic way to explicitly declare an unlock step, the verifier attempts to deduce it. If an adversarial or poorly mapped recipe demands a critical bootloader unlock but renames the prerequisite (e.g., oem_status) and avoids the "unlock" substring in declared_by, the function will classify it as a safe standard condition. The unmarked-unlock-step check is circumvented completely, evaluating to safe despite relying on untested hardware mechanisms.

  FINDINGS
- [ ] flashguard/verify.py:308 _is_unlock_prerequisite introduces undocumented string-matching
  heuristics ("unlock" in declared_by.lower()) to guess if a step is an unlock, masking the absence
  of a formal schema marker and providing a path to a false safe
- [ ] tests/test_verify_v2.py:554 a completely unasked-for RecipePrerequisitesProduceableTest
  was added that analyzes shell scripts and markdown with regex, out of scope for the PR
- [ ] flashguard/verify.py:517 the source.untested fallback is retained as a "deprecated
  fallback" indefinitely with no end date and no writer, exactly as criticized previously
- [ ] data/recipes-v0.2/a5xelte.json:1 the recipe retains a nine-model allowlist while citing
  an upstream config that contains no model strings, leaving its provenance unrecorded
- [ ] tests/test_verify_v2.py:249 the test named for omitting unlock_class still manually
  re-inserts "unlock_step": True, ensuring it passes by supplying the marker it claims to omit
- [ ] tests/test_verify_contract.py:52 test_model_mismatch_is_unsafe_not_abstention still uses
  GD1YQ (which is in the allowlist), passing due to a device mismatch instead of testing models
- [ ] docs/reasoning/verdict-contract.md:123 the specification still formally defines the
  variant field and the safety tiers built on it, although the verifier no longer reads it
- [ ] docs/reasoning/recipe-format-coverage.md:53 the measurement record still tabulates
  target.variant and assets.variant, which no longer exist in the working corpus
- [ ] data/recipe_format_coverage.py:60 the postmarketos row is still matched against
  ^deviceinfo_models=, a key that exists nowhere in the upstream device files
- [ ] flashguard/verify.py:385 product_model is incorrectly appended to fields_consumed before
  validation, falsely asserting the field was verified on execution paths lacking a model list
```

</details>

---


## 2026-09-17 — uncommitted-on-a0713b1 — Batch 5 task

- [ ] `flashguard/verify.py:437` `is_unlock` is now built from `unlock_step`/`is_unlock_step`/
      `unlock_class`, so a prerequisite named `bootloader_unlocked` carrying none of them is
      no longer treated as an unlock and reaches `safe`; `avicii.json`
      returns `safe` (HEAD returned `cannot-verify`) against its own `expected_verdict`
- [ ] `data/recipes-v0.2/avicii.json:1` the recipe still declares `expected_verdict`
      `cannot-verify` and `human_assessment` `unsafe`, and the working-tree verifier now
      answers `safe` for a fingerprint that merely confirms `unlocked`
- [ ] `flashguard/verify.py:422` the unlock marker is satisfied by the mere presence of
      `unlock_class`, and a second alias `is_unlock_step` is accepted here and at `:439`
      that appears in no recipe, schema, test or document
- [ ] `flashguard/verify.py:354` `product_model` is appended to `fields_consumed` before the
      models-list check, so a recipe with no list records the field as consumed on a path
      where no model comparison happened — the same evidence-stamp defect as the
      `variant` entry of 13 September
- [ ] `flashguard/verify.py:511` `in (False, "unestablished", None)` also accepts numeric
      `0`, which is outside the vocabulary the comment above it states; a hand-written
      `0` silently means "not untested" and permits `safe`
- [ ] `docs/reasoning/verdict-contract.md:157` documents `"not_untested"` as a permitted
      value with no effect, but the verifier returns `cannot-verify` with
      `recipe-untested-unrecognized` for it
- [ ] `flashguard/verify.py:497` the `source.untested` fallback is kept without a sunset
      date and with nothing that writes it, which is the second-name problem this change
      exists to remove
- [ ] `docs/reasoning/recipe-format.md:80` claims an omitted `unlock_class` abstains, which
      is false unless the prerequisite also carries the marker; the recipe reaches `safe`
- [ ] `tests/test_verify_v2.py:263` the test named for the rename re-inserts `unlock_step`,
      so it does not exercise the behaviour it is named after; delete that line and it fails
- [ ] `tests/test_verify_contract.py:50` `test_model_mismatch_is_unsafe_not_abstention` uses
      a model that is in the allowlist, so the `unsafe` comes from the device mismatch and
      no model mismatch is tested
- [ ] `data/recipes-v0.2/a5xelte.json:1` the nine-model allowlist that now decides
      `unsafe` cites a source containing no model strings and does not match the only
      upstream file that lists models for this codename
- [ ] `docs/reasoning/verdict-contract.md:123` the specification still defines `variant`
      and the tiers built on it, while the verifier no longer reads any such field
- [ ] `docs/reasoning/recipe-format-coverage.md:53` the measurement record still tabulates
      `target.variant` and `assets.variant`, which no longer exist, against a script that
      now emits `target.models`
- [ ] `data/recipe_format_coverage.py:60` the postmarketOS row is matched on
      `^deviceinfo_models=`, a key that exists nowhere in the checkout, so the row reports
      zero for a naming error rather than a fact
- [ ] `data/coverage.py:109` the false-safe gate counts only `expected == "unsafe"`, so a
      recipe whose `expected_verdict` is `cannot-verify` can return `safe` unremarked

<details><summary>the review, as it came back</summary>

```
Read , lines 345 to 345

Read , lines 375 to 470

Read , lines 445 to 498

Read , lines 544 to 544

Read , lines 530 to 544

Read , lines 520 to 540

Read , lines 540 to 544

Read , lines 544 to 544

Read , lines 540 to 544

Ran terminal command:  cd <repo> && python3 - <<'PY'
import copy, sys, json
sys.path.insert(0,'.')
from flashguard import verify
BASE = json.load(open('tests/test_verify_v2.py').read().split('BASE_RECIPE = ')[1].split('\n\n\ndef fingerprint')[0].replace('True','true').replace('False','false')) if False else None
PY
echo "skip"; git ls-files data/recipes-v0.2/

Ran terminal command:  git status --porcelain | head -40

Ran terminal command:  cd <repo> && python3 - <<'PY'
import sys, json
sys.path.insert(0, '.')
from flashguard import verify

recipe = {
  "schema_version": "0.2",
  "recipe_id": "rename-without-marker",
  "source": {"device_facts_from": "synthetic", "consulted": "2026-09-16",
             "authored": "independent", "upstream_untested": "unestablished"},
  "target": {"product_device": "spacewar", "models": ["A063"], "partition_scheme": "virtual_A/B"},
  "install_method": "fastboot_nexus",
  "prerequisites": {
    "oem_unlocking_enabled": {
      "state": "OPEN", "required": "unlocked",
      "declared_by": "unlock_bootloader",
      "source_evidence": "synthetic setting",
    }
  },
  "operations": [{"kind": "boot-recovery", "partition": "boot"}],
  "source_fields_unused": [],
}
fp = {"product_device": "spacewar", "product_model": "A063",
      "partition_scheme": "virtual_A/B", "oem_unlocking_enabled": "unlocked"}
r = verify(fp, recipe)
print("A. renamed prerequisite, NO marker at all ->", r["verdict"])
print("   codes:", [x["code"] for x in r["reasons"]])

# same, but with unlock_class: "unknown" side by side, for contrast
r2 = dict(recipe); r2["prerequisites"] = {"oem_unlocking_enabled": dict(recipe["prerequisites"]["oem_unlocking_enabled"], unlock_class="command")}
print("B. same with unlock_class command       ->", verify(fp, r2)["verdict"])
PY

Read , lines 1 to 80

Ran terminal command:  grep -n "is_unlock\|has_marked_unlock_step\|has_unlock_operation\|unlock_step\|source.untested\|_UNLOCK" flashguard/verify.py

Ran terminal command:  cd <repo> && python3 - <<'PY'
import sys, os, json
sys.path.insert(0,'.')
sys.argv=['x']
import importlib.util
spec = importlib.util.spec_from_file_location("cov", "data/coverage.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
for label, d in (("v0.1","data/recipes"), ("v0.2","data/recipes-v0.2")):
    for run in m.corpus_runs(os.path.join(d)):
        print("%-5s %-28s expected=%-13s verdict=%-13s paired=%s" % (label, run["recipe_id"], run["expected"], run["verdict"], run["paired"]))
PY

Ran terminal command:  python3 data/coverage.py 2>&1 | grep -n -i "false safe" -B4 -A4

Ran terminal command:  cd <repo> && python3 - <<'PY' 2>&1 | sed -n '1,40p'
import sys, json, copy
sys.path.insert(0, '.')
from flashguard import verify

avicii = json.load(open('data/recipes-v0.2/avicii.json'))
fp = {"product_device":"avicii","product_model":"AC2001","partition_scheme":"A/B",
      "bootloader_unlocked":"unlocked","android_version":12}
r = verify(fp, avicii)
print("avicii-v2, matching fingerprint ->", r["verdict"])
print("  codes:", [x["code"] for x in r["reasons"]])

# numeric zero typo in the untested field
base = json.load(open('tests/../data/recipes-v0.2/spacewar.json'))
b = copy.deepcopy(base)
for val in (0, False, "unestablished"):
    b["source"]["upstream_untested"] = val
    fp2 = {"product_device":"Spacewar","product_model":"A063","partition_scheme":"virtual_A/B",
           "bootloader_unlocked":"unlocked"}
    print("upstream_untested=%-14r ->" % (val,), verify(fp2, b)["verdict"])
PY

Ran terminal command:  grep -rn "recipes-v0.2" docs/INDEX.md OPEN.md 2>/dev/null; echo "--- variant_confirmed_by writers ---"; grep -rn "variant_confirmed_by" bench-kit/ tests/ data/ 2>/dev/null | head -20; echo "--- coverage gate lines ---"; grep -n "def enforce_false_safe_gate" -A6 data/coverage.py; echo "--- not_untested refs ---"; grep -rn "not_untested" --include=*.py --include=*.md . 2>/dev/null | grep -v "^./library" | head

Ran terminal command:  echo "== verify.py =="; grep -n "observed_model = fingerprint.get\|fields_consumed.append("product_model")\|has_unlock_operation\|has_marked_unlock_step\|is_unlock = isinstance\|if is_unlock and unlock_class\|upstream_untested in (False\|source.untested is retained\|Ruled by Ranaji\|Assets in v0.1 are pinned" flashguard/verify.py; echo "== coverage.py gate =="; sed -n '106,112p' data/coverage.py; echo "== recipe-format.md =="; grep -n "model or variant\|models\|unlock_class\|unlock_method" docs/reasoning/recipe-format.md; echo "== verdict-contract =="; grep -n "not_untested" docs/reasoning/verdict-contract.md; echo "== recipe-format-coverage.md =="; grep -n "target.variant\|assets.variant" docs/reasoning/recipe-format-coverage.md; echo "== recipe_format_coverage.py =="; grep -n "models\|target.models\|assets.variant" data/recipe_format_coverage.py

Ran terminal command:  cd <repo> && mkdir -p /tmp/fg_review && git show HEAD:flashguard/verify.py > /tmp/fg_review/verify_head.py && git show HEAD:flashguard/guidance.py > /tmp/fg_review/guidance.py && sed -i '' 's/^from flashguard.guidance/from guidance/' /tmp/fg_review/verify_head.py && python3 - <<'PY'
import sys, json
sys.path.insert(0, '/tmp/fg_review')
sys.path.insert(0, '.')
import importlib.util
spec = importlib.util.spec_from_file_location("vhead", "/tmp/fg_review/verify_head.py")
head = importlib.util.module_from_spec(spec); spec.loader.exec_module(head)
from flashguard import verify as now

avicii = json.load(open('data/recipes-v0.2/avicii.json'))
fp = {"product_device":"avicii","product_model":"AC2001","partition_scheme":"A/B",
      "bootloader_unlocked":"unlocked","android_version":12}
print("avicii-v2 @HEAD  ->", head.verify(fp, avicii)["verdict"])
print("avicii-v2 @now   ->", now(fp, avicii)["verdict"])

# a prerequisite named bootloader_unlocked with no unlock_class and no marker
r = json.loads(json.dumps(avicii))
print("now codes:", [x["code"] for x in now(fp, r)["reasons"]])
PY

Ran terminal command:  ls ../library 2>/dev/null | head; echo "== deviceinfo_models upstream =="; grep -rl "^deviceinfo_models=" ../library/upstream/pmaports 2>/dev/null | head -3; grep -rh "^deviceinfo_[a-z_]*=" ../library/upstream/pmaports 2>/dev/null | sed 's/=.*//' | sort -u | head -40; echo "== is_unlock_step =="; grep -rn "is_unlock_step" --include=*.py --include=*.json --include=*.md . 2>/dev/null | grep -v library | head; echo "== source.untested writers =="; grep -rn '"untested"' data/ tests/ 2>/dev/null | head

Ran terminal command:  grep -rh "^deviceinfo_" ../library/upstream/pmaports --include=deviceinfo 2>/dev/null | sed 's/=.*//' | sort -u | grep -i "model\|variant"; echo "== count =="; grep -rh "^deviceinfo_models\|^deviceinfo_variant" ../library/upstream/pmaports --include=deviceinfo 2>/dev/null | wc -l; echo "== git log for recipes-v0.2 =="; git log --oneline -3 -- data/recipes-v0.2/ | cat; echo "== doc references to recipes-v0.2 =="; grep -rn "recipes-v0.2" --include=*.md --include=*.sh --include=*.html . 2>/dev/null | grep -v library | head

Ran terminal command:  cd <repo> && python3 - <<'PY'
import sys, json, copy
sys.path.insert(0,'.')
from flashguard import verify
BASE = json.loads(open('tests/test_verify_v2.py').read().split('BASE_RECIPE = ')[1].split('\n\n\ndef fingerprint')[0])
# The test as shipped
r = copy.deepcopy(BASE); r["prerequisites"] = {"oem_unlocking_enabled": {
  "state":"OPEN","required":"unlocked","unlock_step":True,
  "declared_by":"unlock_bootloader","source_evidence":"synthetic setting"}}
fp = {"product_device":"spacewar","product_model":"A063","partition_scheme":"virtual_A/B",
      "oem_unlocking_enabled":"unlocked"}
print("as shipped in the test (unlock_step present):", verify(fp, r)["verdict"])
# Same test with ONLY the rename, which is what its docstring describes
r2 = copy.deepcopy(BASE); r2["prerequisites"] = {"oem_unlocking_enabled": {
  "state":"OPEN","required":"unlocked",
  "declared_by":"unlock_bootloader","source_evidence":"synthetic setting"}}
print("docstring's change alone (rename, no marker):  ", verify(fp, r2)["verdict"])
print("   codes:", [x["code"] for x in verify(fp, r2)["reasons"]])
PY

Ran terminal command:  grep -rn "FALSE SAFE" --include=*.py --include=*.sh . 2>/dev/null | grep -v library

Ran terminal command:  cd <repo> && sed -n '205,225p' data/coverage.py; echo "== corpus runs over all dirs =="; python3 - <<'PY'
import sys, os, importlib.util
sys.path.insert(0,'.')
sys.argv=['x']
spec = importlib.util.spec_from_file_location("cov", "data/coverage.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
runs = m.corpus_runs("data/recipes")
print("v0.1 run keys:", runs[0])
print("expected values:", sorted({r["expected"] for r in runs}))
PY

Ran terminal command:  echo "== verdict-contract sections =="; grep -n "^## \|variant\|unlock_class\|unlock_step" docs/reasoning/verdict-contract.md; echo; echo "== test line numbers =="; sed -n '256,276p' tests/test_verify_v2.py | cat -n

Ran terminal command:  grep -rn "coverage.py\|corpus_runs\|report_corpus_runs" tests/*.sh tests/*.py 2>/dev/null | head -20; echo "== all.sh =="; cat tests/all.sh

Ran terminal command:  grep -n "FALSE SAFE\|coverage\|corpus\|verify" tests/review-packet.sh | head -30

Ran terminal command:  bash tests/review-packet.sh 2>/dev/null | sed -n '/--- suite ---/,/--- files touched ---/p'

Ran terminal command:  grep -n "suite\|verify\|coverage\|bash tests\|python3" tests/review-packet.sh

Ran terminal command:  grep -rn "BUILD MUST FAIL" . --include='*' 2>/dev/null | grep -v '^./library' | grep -v Binary | head

Ran terminal command:  bash tests/all.sh 2>&1 | grep -n -B12 -A3 "FALSE SAFE"

Ran terminal command:  grep -n "a5xelte lists eight\|lists eight" docs/Research/TASK-3-variant-danger.md docs/Research/variant-danger-findings.md; echo "== a5xelte model count =="; python3 -c "import json;d=json.load(open('data/recipes-v0.2/a5xelte.json'));print(len(d['target']['models']), d['target']['models'])"; echo "== unmarked prereq repro summary =="; grep -n "unlock_step" flashguard/verify.py data/recipes-v0.2/*.json docs/reasoning/*.md 2>/dev/null

Ran terminal command:  cd <repo> && python3 - <<'PY'
import sys, json, importlib.util
sys.path.insert(0, '/tmp/fg_review'); sys.path.insert(0, '.')
spec = importlib.util.spec_from_file_location("vhead", "/tmp/fg_review/verify_head.py")
head = importlib.util.module_from_spec(spec); spec.loader.exec_module(head)
from flashguard import verify as now
avicii = json.load(open('data/recipes-v0.2/avicii.json'))
fp = {"product_device":"avicii","product_model":"AC2001","partition_scheme":"A/B",
      "bootloader_unlocked":"unlocked","android_version":12}
fp_variant = dict(fp, variant="avicii")
print("HEAD, fp as the capture would name it :", head.verify(fp, avicii)["verdict"])
print("HEAD, fp with variant added          :", head.verify(fp_variant, avicii)["verdict"])
print("now,  fp as the capture would name it:", now(fp, avicii)["verdict"])
PY

Ran terminal command:  grep -rn "coverage" tests/*.sh tests/*.py 2>/dev/null | grep -v test_false_safe_gate | head; echo "== who prints it =="; for f in tests/*.sh tests/*.py tests/*.js; do if grep -q "coverage" "$f" 2>/dev/null; then echo "-- $f"; fi; done; echo "== run.sh tail =="; tail -20 tests/run.sh

Read , lines 38 to 72

Ran terminal command:  cd <repo> && python3 - <<'PY'
import sys, json, copy
sys.path.insert(0, '.')
from flashguard import verify
space = json.load(open('data/recipes-v0.2/spacewar.json'))
fp = {"product_device":"Spacewar","product_model":"A063","partition_scheme":"virtual_A/B",
      "bootloader_unlocked":"unlocked"}
for v in (False, "not_untested", "unestablished"):
    r = copy.deepcopy(space); r["source"]["upstream_untested"] = v
    out = verify(fp, r)
    print("upstream_untested=%-14r -> %-13s %s" % (v, out["verdict"], [x["code"] for x in out["reasons"] if x["result"]=="abstain"]))
PY

Ran terminal command:  cd <workspace> && find library/upstream/openandroidinstaller -name "a5xelte.yaml" 2>/dev/null | head -2; python3 - <<'PY'
import re
p = "library/upstream/openandroidinstaller/openandroidinstaller/assets/configs/a5xelte.yaml"
try:
    t = open(p).read()
except FileNotFoundError:
    import glob
    hits = glob.glob("library/upstream/openandroidinstaller/**/a5xelte.yaml", recursive=True)
    print("found:", hits); p = hits[0] if hits else None
    t = open(p).read() if p else ""
if t:
    # print only the field-name lines, not prose
    for line in t.splitlines():
        s = line.strip()
        if re.match(r'^(supported_device_codes|variant|models|device_models|codename)\b', s) or s.startswith("- "):
            print(repr(s[:80]))
PY

Ran terminal command:  cd <workspace> && python3 - <<'PY'
import glob, re, json
hits = glob.glob("library/upstream/lineage_wiki/_data/devices/a5xelte.yml")
print("lineage file:", hits)
if hits:
    t = open(hits[0]).read()
    for line in t.splitlines():
        s = line.strip()
        if re.match(r'^models:', s) or (s.startswith('- ') and 'SM-' in s):
            print(repr(s[:80]))
print("---- spacewar ----")
h2 = glob.glob("library/upstream/lineage_wiki/_data/devices/*acewar*.yml") + glob.glob("library/upstream/lineage_wiki/_data/devices/Spacewar.yml")
print(h2)
PY

Ran terminal command:  cd <workspace> && python3 - <<'PY'
import glob, re
t = open("library/upstream/lineage_wiki/_data/devices/a5xelte.yml").read()
for line in t.splitlines():
    if line.strip().startswith("models:"):
        val = line.split("models:",1)[1].strip()
        print("raw:", val)
        items = [x.strip() for x in val.strip("[]").split(",")]
        print("count upstream:", len(items))
        print(items)
PY

Ran terminal command:  cd <repo> && grep -n "diff\|git " tests/review-packet.sh | head -20; echo "== a5xelte recipe line/col of models =="; grep -n "models" docs/reasoning/recipe-format-coverage.md | head -5; echo "== deviceinfo key count =="; grep -rh "^deviceinfo_" ../library/upstream/pmaports --include=deviceinfo 2>/dev/null | sed 's/=.*//' | sort -u | wc -l

Ran terminal command:  cd <workspace> && grep -rh "^deviceinfo_variant" library/upstream/pmaports --include=deviceinfo 2>/dev/null | wc -l; grep -rh "^deviceinfo_models" library/upstream/pmaports --include=deviceinfo 2>/dev/null | wc -l; echo "== oai device_models/device_models keys =="; grep -rh "^ *\(device_models\|device_model\|supported_device_codes\|models\):" library/upstream/openandroidinstaller/openandroidinstaller/assets/configs/*.yaml 2>/dev/null | sed 's/:.*//' | sort | uniq -c; echo "== lineage models count =="; grep -rl "^models:" library/upstream/lineage_wiki/_data/devices 2>/dev/null | wc -l

Ran terminal command:  cd <repo> && cat > /tmp/fg_review/check.py <<'PY'
import sys, json, copy
sys.path.insert(0, '<repo>')
from flashguard import verify

BASE = {
    "schema_version": "0.2",
    "recipe_id": "spacewar-unlock-aware",
    "source": {"device_facts_from": "synthetic", "consulted": "2026-09-08",
               "authored": "independent", "upstream_untested": "unestablished"},
    "target": {"product_device": "spacewar", "models": ["A063"],
               "partition_scheme": "virtual_A/B"},
    "install_method": "fastboot_nexus",
    "prerequisites": {
        "bootloader_unlocked": {
            "state": "OPEN", "required": "unlocked", "unlock_class": "command",
            "declared_by": "unlock_bootloader",
            "source_evidence": "synthetic config unlock step"}},
    "operations": [{"kind": "write-image", "partition": "system"}],
    "source_fields_unused": [],
}
FP = {"product_device": "spacewar", "product_model": "A063",
      "partition_scheme": "virtual_A/B", "bootloader_unlocked": "unlocked"}

# Exactly what the shipped test describes: rename, omit unlock_class.
r = copy.deepcopy(BASE)
pre = dict(BASE["prerequisites"]["bootloader_unlocked"])
pre.pop("unlock_class")
r["prerequisites"] = {"oem_unlocking_enabled": pre}
fp = dict(FP); fp.pop("bootloader_unlocked"); fp["oem_unlocking_enabled"] = "unlocked"
out = verify(fp, r)
print("rename + omit unlock_class, NO marker  ->", out["verdict"])
print("   abstain codes:", [x["code"] for x in out["reasons"] if x["result"] == "abstain"])

# What the shipped test actually constructs: it re-adds unlock_step.
r2 = copy.deepcopy(r)
r2["prerequisites"]["oem_unlocking_enabled"]["unlock_step"] = True
out2 = verify(fp, r2)
print("same, with unlock_step added back      ->", out2["verdict"])

# The checked-in corpus recipe, unmarked unlock prerequisite.
avicii = json.load(open('<repo>/data/recipes-v0.2/avicii.json'))
av_fp = {"product_device": "avicii", "product_model": "AC2001",
         "partition_scheme": "A/B", "bootloader_unlocked": "unlocked",
         "android_version": 12}
print("avicii.json, matching fingerprint      ->", verify(av_fp, avicii)["verdict"])
PY
python3 /tmp/fg_review/check.py

Ran terminal command:  python3 /tmp/fg_review/check.py 2>&1 | tail -8

Ran terminal command:  cd <repo> && python3 -c "
import sys, json, copy
sys.path.insert(0,'.')
from flashguard import verify
B={'schema_version':'0.2','recipe_id':'x','source':{'device_facts_from':'s','consulted':'2026-09-08','authored':'independent','upstream_untested':'unestablished'},'target':{'product_device':'spacewar','models':['A063'],'partition_scheme':'virtual_A/B'},'install_method':'fastboot_nexus','prerequisites':{'bootloader_unlocked':{'state':'OPEN','required':'unlocked','unlock_class':'command','declared_by':'unlock_bootloader','source_evidence':'s'}},'operations':[{'kind':'write-image','partition':'system'}],'source_fields_unused':[]}
FP={'product_device':'spacewar','product_model':'A063','partition_scheme':'virtual_A/B','oem_unlocking_enabled':'unlocked'}
r=copy.deepcopy(B); pre=dict(B['prerequisites']['bootloader_unlocked']); pre.pop('unlock_class'); r['prerequisites']={'oem_unlocking_enabled':pre}
o=verify(FP,r); print('rename+omit class, NO marker ->',o['verdict'],[x['code'] for x in o['reasons'] if x['result']=='abstain'])
r2=copy.deepcopy(r); r2['prerequisites']['oem_unlocking_enabled']['unlock_step']=True
print('same WITH unlock_step added ->',verify(FP,r2)['verdict'])
a=json.load(open('data/recipes-v0.2/avicii.json')); f2={'product_device':'avicii','product_model':'AC2001','partition_scheme':'A/B','bootloader_unlocked':'unlocked','android_version':12}
print('avicii.json matching fp ->',verify(f2,a)['verdict'])
"

Ran terminal command:  grep -n "product_model\|models-unestablished\|"models" not in target\|asset-product_device-mismatch\|Assets in v0.1\|deprecated fallback\|upstream_untested in (False\|unmarked-unlock-step\|is_unlock = isinstance\|has_marked_unlock_step\|source.untested" flashguard/verify.py

Ran terminal command:  cd <workspace> && grep -rl "SM-A510FD" library/upstream/ 2>/dev/null | head -5; echo "--- count of files mentioning SM-A510FD ---"; grep -rl "SM-A510FD" library/upstream/ 2>/dev/null | wc -l; echo "--- a5xelte.yaml model-ish tokens ---"; grep -o "SM-A510[A-Z0-9/]*" library/upstream/openandroidinstaller/openandroidinstaller/assets/configs/a5xelte.yaml | sort -u; echo "--- spacewar lineage models ---"; grep -h "^models:" library/upstream/lineage_wiki/_data/devices/Spacewar.yml

Ran terminal command:  cd <workspace> && for d in FP3 FP4 avicii kirin; do f=$(ls library/upstream/lineage_wiki/_data/devices/$d.yml 2>/dev/null | head -1); if [ -n "$f" ]; then printf "%-8s %s\n" "$d" "$(grep -h '^models:' $f)"; else echo "$d: no lineage page"; fi; done; echo "--- recipe lists ---"; python3 -c "
import json
for n in ('fp3','fp4','avicii','kirin','a5xelte','spacewar'):
    d=json.load(open('project/data/recipes-v0.2/%s.json'%n))
    print('%-9s %s' % (n, d['target']['models']))
"

Ran terminal command:  cd <repo> && python3 -c "
import sys, json
sys.path.insert(0,'.')
from flashguard import verify
# v0.2 recipe with NO models list at all
r={'schema_version':'0.2','recipe_id':'x','source':{'device_facts_from':'s','consulted':'2026-09-08','authored':'independent','upstream_untested':'unestablished'},'target':{'product_device':'spacewar','partition_scheme':'virtual_A/B'},'install_method':'fastboot_nexus','prerequisites':{'bootloader_unlocked':{'state':'OPEN','required':'unlocked','unlock_class':'command','declared_by':'unlock_bootloader','source_evidence':'s'}},'operations':[{'kind':'write-image','partition':'system'}],'source_fields_unused':[]}
fp={'product_device':'spacewar','partition_scheme':'virtual_A/B','bootloader_unlocked':'unlocked'}
out=verify(fp,r)
print('verdict:',out['verdict'])
print('reasons involving model:',[x for x in out['reasons'] if 'model' in x['code']])
print('fields_consumed:',out['evidence']['fields_consumed'])
"

Ran terminal command:  cd <workspace> && grep -rh "^deviceinfo_" library/upstream/pmaports --include=deviceinfo 2>/dev/null | sed 's/=.*//' | sort -u | grep -i "name\|codename\|chassis\|device\b" ; echo "--- any key containing 'model' anywhere in pmaports ---"; grep -rho "^deviceinfo_[a-z_]*model[a-z_]*" library/upstream/pmaports --include=deviceinfo 2>/dev/null | sort -u | head

Ran terminal command:  cd <repo> && echo "== test_verify_v2.py =="; grep -n "unlock_step\|def test_renamed_unlock\|Rename unlock prerequisite to oem" tests/test_verify_v2.py; echo; echo "== verify.py =="; grep -n "has_unlock_operation = any\|unmarked-unlock-step\|if is_unlock and unlock_class\|required = requirement.get" flashguard/verify.py; echo; echo "== recipe-format.md =="; grep -n "Absence of .unlock_class" docs/reasoning/recipe-format.md; echo; echo "== verdict-contract.md variant section =="; sed -n '121,142p' docs/reasoning/verdict-contract.md | head -5; echo; echo "== recipe-format-coverage.md rows =="; grep -n "target.variant\|assets.variant" docs/reasoning/recipe-format-coverage.md | head -3

Ran terminal command:  cd <repo> && grep -n "product_model\|def test_model_mismatch\|product_device.*cheetah\|models" tests/test_verify_contract.py; echo "== recipe line refs =="; python3 -c "
import json
d=json.load(open('data/recipes-v0.2/avicii.json'))
print('avicii prereq keys:', list(d['prerequisites']['bootloader_unlocked'].keys()))
print('avicii source:', d['source'])
print()
a=json.load(open('data/recipes-v0.2/a5xelte.json'))
print('a5xelte source:', a['source'])
"

I read `copilot-instructions.md`, `verifier-plan.md`, `verdict-contract.md`, `recipe-format.md`, the verifier, the recipes and the tests, and I reproduced the cases below against the working tree.

## 1. What changed that was not asked for?

Beyond swapping `variant` for a `models` allowlist, the diff adds four things nothing in the surrounding format asked for:

- **A second name for the unlock marker**: `is_unlock_step` is accepted at `flashguard/verify.py:422` and `:439`. It appears in no recipe, no test, no doc, and no schema — the diff introduces two spellings of a safety field in the same commit that exists to collapse `upstream_untested`/`untested` into one.
- **The `source.untested` fallback survives** at `flashguard/verify.py:497-503`, with a comment giving no expiry and no writer anywhere.
- **A widening of what permits `safe`**: `upstream_untested in (False, "unestablished", None)` at `:511` also accepts numeric `0`, which is outside the vocabulary the diff's own comment states.
- **`models` written into the five v0.1 corpus recipes** (`data/recipes/*.json`), which is a consequence of removing `variant`, but it also changes what the v0.1 corpus can express; `recipe-format-coverage.md` was not updated to match.

Also present and unmentioned in the packet's file list: `spacewar.json` is untracked and is not named in `INDEX.md`.

## 2. What did it decide that was not already in a file?

- **That an unlock prerequisite without a marker is verifiable.** `flashguard/verify.py:437` defines `is_unlock` from `unlock_step`/`is_unlock_step`/`unlock_class`. A prerequisite named `bootloader_unlocked` that carries none of them is no longer an unlock at all, and falls through to the ordinary required-state check. No file says this; `docs/reasoning/recipe-format.md:80` still says the opposite.
- **That `unlock_class` counts as proof of an unlock step** (`:422`), so the new `unmarked-unlock-step` reason is not reachable for any recipe that declares one anywhere.
- **The `is_unlock_step` alias and the permanent `untested` fallback** — decisions made in code, in no document.
- **That a numeric `0` is an acceptable "not untested"** — again code only.
- **The nine-model `a5xelte` allowlist.** The allowlist is now what decides `unsafe`, and `source.device_facts_from` for that recipe cites the OpenAndroidInstaller config, which contains no model strings at all; the only file in the checkout that lists models for this codename lists eight different strings. The decision about which hardware this recipe may touch has no recorded provenance.

## 3. Does any test pass for a reason other than the code being correct?

Yes, two.

- `tests/test_verify_v2.py:256-263`. Its docstring says "Rename unlock prerequisite to `oem_unlocking_enabled`, omit `unlock_class`", but line 263 re-inserts `"unlock_step": True`. With that line removed the recipe returns **`safe`** with `prerequisite-oem_unlocking_enabled-confirmed` and no abstention. The test passes because it supplies the marker the fix depends on, not because the rename is handled.
- `tests/test_verify_contract.py:50`. `test_model_mismatch_is_unsafe_not_abstention` uses a fingerprint whose `product_model` is `GD1YQ`, which *is* in `SAFE_RECIPE`'s list. The `unsafe` comes from `product_device: "cheetah"` vs `"oriole"` — a device mismatch. The test never exercises a model mismatch.

## 4. Does any file, name or comment describe something as existing that does not?

- `docs/reasoning/recipe-format.md:80` — "Absence of `unlock_class` is not `command`: an omitted field abstains with the generic missing prerequisite reason." Reproduced false: omit `unlock_class` (and the marker) and the verifier returns `safe`, not `cannot-verify`.
- `docs/reasoning/verdict-contract.md:123-141` — the "Graded variant matching" section still specifies a recipe/fingerprint field called `variant` and tiers built on it. The verifier no longer reads any such field.
- `docs/reasoning/recipe-format-coverage.md:53,59,79,85,105,111` — still tabulates `target.variant` and `assets.variant`, which no longer exist, while `data/recipe_format_coverage.py:81` now emits `target.models`. The doc and the script no longer describe the same fields.
- `data/recipe_format_coverage.py:60` — the renamed row is computed from `^deviceinfo_models=`, and no `deviceinfo_models` key exists anywhere in the postmarketOS checkout (the field-name census over `deviceinfo` keys has 164 keys, none matching). The row reads zero because the pattern names a key upstream does not have, not because the sources lack models.
- `flashguard/verify.py:497` — "retained as a deprecated fallback during the v0.1 -> v0.2 transition", with no end to the transition written down and nothing that writes `source.untested`.

## 5. Does anything here create a path to a false `safe`?

Yes, and it is a regression, not a pre-existing hole.

On `avicii.json` with the fingerprint `{product_device: avicii, product_model: AC2001, partition_scheme: A/B, bootloader_unlocked: unlocked, android_version: 12}`:

    verifier at HEAD          -> cannot-verify
    verifier in working tree  -> safe
    reasons: match-product_device, match-partition_scheme, match-product_model,
             prerequisite-bootloader_unlocked-confirmed, prerequisite-android_version-confirmed

That recipe carries `expected_verdict: cannot-verify` and `human_assessment: unsafe`, and its unlock prerequisite has no `unlock_class`. At HEAD the hard-coded `_UNLOCK_PREREQUISITE_NAME` made it abstain; removing that constant without the marker being present on existing recipes removed the protection. The `unmarked-unlock-step` gate at `:425` cannot help, because it fires only when the recipe declares an `unlock_bootloader` *operation*, which no recipe in the corpus does.

Second path, smaller but real: `upstream_untested` set to `0` returns `safe`, because `0 == False` at `:511`. The stated rule is that only an explicit `false` and `"unestablished"` permit; a hand-written zero currently does.

And the gate that would have made this visible is `data/coverage.py:109`, which counts a false safe only when `expected == "unsafe"`. A recipe whose own `expected_verdict` is `cannot-verify` can return `safe` and no check says a word.

Everything else I looked for was clean: the model check fails closed on exact-string membership, an absent model and an absent list both abstain, `unsafe` still outranks abstention, and the v0.1 asset rule is still an `unsafe` on mismatch.

  FINDINGS
  - [ ] `flashguard/verify.py:437` `is_unlock` is now built from `unlock_step`/`is_unlock_step`/
        `unlock_class`, so a prerequisite named `bootloader_unlocked` carrying none of them is
        no longer treated as an unlock and reaches `safe`; `avicii.json`
        returns `safe` (HEAD returned `cannot-verify`) against its own `expected_verdict`
  - [ ] `data/recipes-v0.2/avicii.json:1` the recipe still declares `expected_verdict`
        `cannot-verify` and `human_assessment` `unsafe`, and the working-tree verifier now
        answers `safe` for a fingerprint that merely confirms `unlocked`
  - [ ] `flashguard/verify.py:422` the unlock marker is satisfied by the mere presence of
        `unlock_class`, and a second alias `is_unlock_step` is accepted here and at `:439`
        that appears in no recipe, schema, test or document
  - [ ] `flashguard/verify.py:354` `product_model` is appended to `fields_consumed` before the
        models-list check, so a recipe with no list records the field as consumed on a path
        where no model comparison happened — the same evidence-stamp defect as the
        `variant` entry of 13 September
  - [ ] `flashguard/verify.py:511` `in (False, "unestablished", None)` also accepts numeric
        `0`, which is outside the vocabulary the comment above it states; a hand-written
        `0` silently means "not untested" and permits `safe`
  - [ ] `docs/reasoning/verdict-contract.md:157` documents `"not_untested"` as a permitted
        value with no effect, but the verifier returns `cannot-verify` with
        `recipe-untested-unrecognized` for it
  - [ ] `flashguard/verify.py:497` the `source.untested` fallback is kept without a sunset
        date and with nothing that writes it, which is the second-name problem this change
        exists to remove
  - [ ] `docs/reasoning/recipe-format.md:80` claims an omitted `unlock_class` abstains, which
        is false unless the prerequisite also carries the marker; the recipe reaches `safe`
  - [ ] `tests/test_verify_v2.py:263` the test named for the rename re-inserts `unlock_step`,
        so it does not exercise the behaviour it is named after; delete that line and it fails
  - [ ] `tests/test_verify_contract.py:50` `test_model_mismatch_is_unsafe_not_abstention` uses
        a model that is in the allowlist, so the `unsafe` comes from the device mismatch and
        no model mismatch is tested
  - [ ] `data/recipes-v0.2/a5xelte.json:1` the nine-model allowlist that now decides
        `unsafe` cites a source containing no model strings and does not match the only
        upstream file that lists models for this codename
  - [ ] `docs/reasoning/verdict-contract.md:123` the specification still defines `variant`
        and the tiers built on it, while the verifier no longer reads any such field
  - [ ] `docs/reasoning/recipe-format-coverage.md:53` the measurement record still tabulates
        `target.variant` and `assets.variant`, which no longer exist, against a script that
        now emits `target.models`
  - [ ] `data/recipe_format_coverage.py:60` the postmarketOS row is matched on
        `^deviceinfo_models=`, a key that exists nowhere in the checkout, so the row reports
        zero for a naming error rather than a fact
  - [ ] `data/coverage.py:109` the false-safe gate counts only `expected == "unsafe"`, so a
        recipe whose `expected_verdict` is `cannot-verify` can return `safe` unremarked
```

</details>

---


## 2026-09-16 — uncommitted-on-5573d4b — Batch 4 task

Nothing found. Recorded because a log of only non-empty reviews is a biased log, and because "has this been reviewed at all" is a question worth being able to answer.

<details><summary>the review, as it came back</summary>

```
FINDINGS
- flashguard/verify.py:459 upstream_untested gate is new behavior not requested; it reads source.untested (a withdrawn/deleted field per deleted unlock_guidance.json) and references upstream testing state that is documented as "pending resolution" rather than decided; the not_untested (false) branch does not upgrade safe, but true does add an abstain reason (correct direction), yet the decision to act on absence as unestablished and on presence as refusal has not been finalized in a file
- docs/reasoning/verdict-contract.md:140 new section records upstream untested flag rules, but the "pending upstream resolution" subsection explicitly says absence-of-flag behavior is unsettled — this is a decision presented as unsettled, not one decided
- tests/test_verify_v2.py (all UpstreamUntestedGateTest): all pass correctly (untested → cannot-verify, not_untested returns identical reasons, absent/unestablished returns identical); the false-safe prevention works; but test_not_untested_recipe_returns_byte_identical_reasons asserts byte-identical reasons for a field value (false) whose effect is documented as "no effect today," which is consistent
- data/unlock_guidance.json deleted and flashguard/guidance.py deleted, but flashguard/verify.py:3 still imports get_guidance and verify.py:399-472 still builds guidance evidence; the import will fail at runtime if guidance.py is genuinely removed, yet the file exists in working tree (git status shows it untracked, not deleted from tree) — this is a discrepancy: the commit deletes it but the working copy keeps it, and the verifier relies on it
- No false-safe path: upstream_untested in (True, ...) always adds an abstain reason, so verdict can never become safe; unsafe (identity/prerequisite mismatch) takes precedence over the abstain because it returns early; this ordering is safe
- tests/test_verify_v2.py:386 test asserts fields_consumed never contains "source" — correct per the contract (fingerprint evidence only), and the new source.upstream_untested reason uses fields (not fields_consumed) for its evidence, which is correct
```

</details>

---


## 2026-09-16 — uncommitted-on-bba77c0 — Batch 3 task + Nothing1 recipe

- [ ] flashguard/verify.py:409 assigning None to required when       requirement is not tion check (requiredis not None), falling through to pass and creating a direct path toa false safe verdic
- [ ] docs/reasoning/recipe-format.md:81 claims that an omitted      unlock_class abstaireason, but the codeskips checking for omission and verifies it identically to a valid requirement.
- [ ] tests/test_verify_v2.py:327 test_omitted_unlock_class_...      passes for the wronletely because themock fingerprint() lacks bootloader_unlocked data, not because the code enforces the o
- [ ] flashguard/verify.py:3 importing get_guidance to supply  out-of-band data sta/unlock_guidance.json from the filesystem on the verify path, violating the strict non-negotiable propain a pure function.

<details><summary>the review, as it came back</summary>

```
Based on a review of the uncommitted diff, here are the answers to your questions:

1. What changed that was not asked for?
   flashguard/verify.py adds if fingerprint is None: fingerprint = {} at the top of _verify_v2. This silently mutates the input to prevent a crash, and appears to have been added solely to support the author's new test patterns (for fp in (None, {}, fingerprint()):) rather than a requested change to the application's contract.
2. What did it decide that was not already in a file?
   The code decided to treat an omitted unlock_class as fully verifiable (identical to "command"), falling through to typical verification loops if the fingerprint possesses the needed field. This directly contradicts the written rule.
3. Does any test pass for a reason other than the code being correct?
   Yes. test_omitted_unlock_class_returns_missing_bootloader_and_not_unlock_out_of_band passes entirely by coincidence. It calls verify(fingerprint(), recipe), but fingerprint() does not contain the bootloader_unlocked key. The test passes because the verification naturally aborts on the missing fingerprint data, not because the verifier successfully handled the omitted unlock_class. If fingerprint("unlocked") had been used, it would have returned safe.
4. Does any file, name or comment describe something as existing that does not?
   Yes. docs/reasoning/recipe-format.md explicitly claims that "an omitted field abstains with the generic missing prerequisite reason." The code does not implement this behavior.
5. Does anything here create a path to a false safe?
   Yes. The change to required = requirement.get("required") if isinstance(requirement, dict) else None is critical. If a recipe mistakenly supplies a string instead of a dictionary (e.g., "bootloader_unlocked": "unlocked"), required is assigned None. The mismatch checker (elif required is not None and observed != required:) will evaluate to false, meaning any observed state on the device will quietly fall through to the else block, record "pass", and return a false safe.

  FINDINGS
- [ ] flashguard/verify.py:409 assigning None to required when       requirement is not tion check (requiredis not None), falling through to pass and creating a direct path toa false safe verdic
- [ ] docs/reasoning/recipe-format.md:81 claims that an omitted      unlock_class abstaireason, but the codeskips checking for omission and verifies it identically to a valid requirement.
- [ ] tests/test_verify_v2.py:327 test_omitted_unlock_class_...      passes for the wronletely because themock fingerprint() lacks bootloader_unlocked data, not because the code enforces the o
- [ ] flashguard/verify.py:3 importing get_guidance to supply  out-of-band data sta/unlock_guidance.json from the filesystem on the verify path, violating the strict non-negotiable propain a pure function.
```

</details>

---


## 2026-09-16 — uncommitted-on-e7ad22c — Added tests for capture route and browser enumeration

- [ ] tests/run-console-logic.js:146 schema agreement checks were added prematurely, violating
      the explicit deferrt asked to wait forthe variant omission decision                                       [ ] tests/run-consoextraction allows thetest to pass vacuously if no                                        assignments happen  since an empty arrayskips the assertion loop                                            [ ] tests/run-consot claims to test"across all capture routes &                                        enumerations" but tndpicked combinations
- [ ] tests/run-console-logic.js:243 the comment "macOS branch with   browser enumeration
      implies the existence of specific branching logic in the builder    that does not exist
- [ ] tests/run-console-logic.js:256 the Linux host platform test was changed from ubuntu
      to ubuntu_live without being asked for and without an accompanying decision in a file

<details><summary>the review, as it came back</summary>

```

1. What changed that was not asked for?
   The agreement checks for capture_route and browser_enumeration were added prematurely. The tracker note in OPEN.md explicitly deferred this step by stating "After that we can run some checks" referring to the variant omission decision being settled first. Additionally, the existing test for Linux was changed from targeting ubuntu_installed to ubuntu_live, which was not requested.
2. What did it decide that was not already in a file?
   It arbitrarily mapped combinations in the testing fixtures, such as deciding the macOS test should represent browser_enumeration: "tester_cancelled" paired with capture_route: "adb_host", and changed the Linux test framework to represent a "Live Linux USB branch" via ubuntu_live. These specific data mappings and mock scenarios were not recorded in any decision file.
3. Does any test pass for a reason other than the code being correct?
   Yes. For both capture_route (line 199) and browser_enumeration (line 206), the tests extract assignments from START-HERE.html using a regex and iterate over the results to assert they are in the schema. If the regex fails to match anything, the resulting arrays are empty, and the for loops execute zero times. This allows the test to silently pass vacuously. (Additionally, the "is rejected by schema" assertions just check if a hardcoded invalid string is missing from a JS Set, not whether the actual validator catches it).
4. Does any file, name or comment describe something as existing that does not?
   Yes. The comment "Test buildRecord / saveRecord resolution across all capture routes & enumerations" (line 215) claims to test all routes and enumerations, but only tests four hardcoded ones. Furthermore, comments referring to "macOS branch with browser enumeration failure / tester_cancelled" (line 243) and "Live Linux USB branch" (line 256) falsely describe static fixtures as if they correspond to specific branching logic in the target code.
5. Does anything here create a path to a false safe?
   No. The changes in this diff are limited to internal test assertions and do not create a path to a false safe in the codebase's verifier.

  FINDINGS
- [ ] tests/run-console-logic.js:146 schema agreement checks were added prematurely, violating
  the explicit deferrt asked to wait forthe variant omission decision                                       [ ] tests/run-consoextraction allows thetest to pass vacuously if no                                        assignments happen  since an empty arrayskips the assertion loop                                            [ ] tests/run-consot claims to test"across all capture routes &                                        enumerations" but tndpicked combinations
- [ ] tests/run-console-logic.js:243 the comment "macOS branch with   browser enumeration
  implies the existence of specific branching logic in the builder    that does not exist
- [ ] tests/run-console-logic.js:256 the Linux host platform test was changed from ubuntu
  to ubuntu_live without being asked for and without an accompanying decision in a file
```

</details>

---


## 2026-09-16 — uncommitted-on-3ed8346 — Batch 2b changes on the BenchKit based on MAC vs windows commands

- [ ] tests/run-console-logic.js:157 the schema validation test merely checks whether a string is present in its own hardcoded Set parsed from the Markdown file, instead of testing any actual schema enforcer, meaning the test asserts a tautology and proves nothing about validation.
- [ ] tests/run-console-logic.js:177 the regex /host_shell\s*[:=]\s*"([^"]+)"/g fails to match the ternary assignment cur.host_shell = isCmd ? "cmd" : "powershell" in the application code, allowing the check to pass without actually validating those assigned values.

<details><summary>the review, as it came back</summary>

```
FINDINGS
- [ ] tests/run-console-logic.js:157 the schema validation test merely checks whether a string is present in its own hardcoded Set parsed from the Markdown file, instead of testing any actual schema enforcer, meaning the test asserts a tautology and proves nothing about validation.
- [ ] tests/run-console-logic.js:177 the regex /host_shell\s*[:=]\s*"([^"]+)"/g fails to match the ternary assignment cur.host_shell = isCmd ? "cmd" : "powershell" in the application code, allowing the check to pass without actually validating those assigned values.
```

</details>

---


## 2026-09-16 — uncommitted-on-dba8e8f — Batch 2 changes on the BenchKit based on research

Nothing found. Recorded because a log of only non-empty reviews is a biased log, and because "has this been reviewed at all" is a question worth being able to answer.

<details><summary>the review, as it came back</summary>

```
Based on my review of the diff against the batch 2 requirements, here are the answers to the 5 review questions:

---

1. What changed in the Windows command block?

The Windows quoting bug is fixed by splitting the shell selection and using correct quoting per shell:

- Added scrWindowsShell() (lines 704–723): A new screen asking "Which shell are you using on Windows?" with two buttons — PowerShell and Command Prompt (cmd). The choice is recorded as windows_powershell or windows_cmd.
- Modified scrRoutePlatform() (lines 725–735): The generic "windows" platform now routes to the shell selection screen instead of directly to scrAndroidRaw().
- Modified scrAndroidRaw() (lines 797–843): Now accepts the specific shell platform and generates different quoting:
  - PowerShell → single-quoted: adb shell 'for p in ...; do echo $p=$(getprop $p); done' — PowerShell treats single quotes as literal, so $p and $(getprop $p) pass through to adb unexpanded
  - cmd → double-quoted: adb shell "for p in ...; do echo $p=$(getprop $p); done" — cmd doesn't expand $, so this already worked
- Fixed the heading (line 808): The kicker now shows the actual shell name (PowerShell or Command Prompt (cmd)) instead of the misleading "PowerShell / cmd" label.

---

2. What was decided about the shell split?

Exactly what batch 2 required:
- The Windows branch  paths(windows_powershell and windows_cmd)
- A second question o the tester's actualshell
- Both command blocksies in the same order(line 801) — ro.product.model is preserved
- The answer is recorwnstream knows whichshell produced the capture

---

3. Are the tests correct?

Yes. The test guard in tests/test-android-raw-agreement.sh (lines
16–22) was restored:
if grep -q "adb shell getprop" "$HTML"; then
  echo "  FAIL: STARTprop commands..."
  fail=1
fi
This asserts that no line of START-HERE.html offers a bare adb shell
getprop <key> (which without keys). Theloop forms (for p in ...; do echo $p=$(getprop $p); done) print
key=value and pass. T to catch bare formsbut loose enough not to fire on the loop forms.

---

4. Any phantom features?

No. Only the two files mentioned in batch 2 changed:
- bench-kit/START-HERection + quoting fix
- tests/test-android-raw-agreement.sh — restored the bare-getprop
  guard

No new screens, no neges, no scope creep.The diff is exactly what batch 2 specified.

---

5. Any false-safe paths?

No false-safe introduced. This is Tier A (data collection UI only).
The verifier (flashgud. The fix actuallyremoves a data-corruption path: previously, PowerShell would expand
$p and $(getprop $p)  producing garbageoutput that isValidRawProps would reject — wasting the tester's time
but not entering the aches the device shell correctly on both shells.

---

Summary: The batch 2 work is complete and correct. bash tests/all.sh passes (the false-safverifier corpus,unrelated to this change). The two PowerShell/cmd strings are stated verbatim in the diff
```

</details>

---






## 2026-09-14 — 251df11 — Second Repair run for WebUSB+Benchkit Integration

- [ ] tests/test-android-raw-agreement.sh:5-6 The old test mechanically guarded against
      re-introduction of bare getprART-HERE.html (grepping
      for adb shell getprop ro.product.manufacturer). That assertion was removed. The
      only remaining guard is the p copilot-instructions.md,
      which is a documentation layer, not a mechanical one.

<details><summary>the review, as it came back</summary>

```
Review of 251df11

1. What changed that was not asked for?

I cannot determine this from the diff alone (no rationale was read, by instruction). Everything in the diff forms a coherent unit: extract two functions, use them in both paste paths, test them in Node, and restructure the bash test from "normalised input matches canonical" to "un-normalised input diverges from canonical". Nothing appears orphaned or unrelated.

2. What did it decide that was not already in a file?

The test architecture split — normalisation correctness in Node, hazard existence in bash — is a structural choice. The header comment at tests/test-android-raw-agreement.sh:4-9 documents it after the fact, but no file records why this split was chosen over the prior design (same-suite agreement checks). This is a test strategy decision made in code, not documented as a decision.

3. Does any test pass for a reason other than the code being correct?

No false passes found. Each test exercises the code it claims to. The bare-values test (line 91 of run-console-logic.js) is fragile to a future fixture whose property value contains both = and a substring matching ro.<word>=, but that is a hypothetical: no current fixture has such a value, and the test label accurately describes what happens with the current data.

4. Does any file, name or comment describe something as existing that does not?

Nothing found. The comment at tests/test-android-raw-agreement.sh:8-9 correctly states that tests/run-console-logic.js tests both functions against all fixtures.

5. Does anything here create a path to a false safe?

No. The diff touches bench-kit data collection and tests. It does not modify flashguard/verify.py, any recipe, any corpus file, or the false-safe gate. normaliseRawProps trims whitespace from property lines before they reach derive.sh, which makes derivation more correct,

---

FINDINGS
- [ ] tests/test-android-raw-agreement.sh:5-6 The old test mechanically guarded against
  re-introduction of bare getprART-HERE.html (grepping
  for adb shell getprop ro.product.manufacturer). That assertion was removed. The
  only remaining guard is the p copilot-instructions.md,
  which is a documentation layer, not a mechanical one.
      RECONSTRUCTED 16 September, not rewritten: the text above arrived corrupted mid-line ("bare getprART-HERE.html", "the p copilot-instructions.md"), which is the filer's truncation guard catching a cut-off END but not a cut-out MIDDLE. Left as filed, because a reviewer's words are evidence. What it means: the grep in tests/test-android-raw-agreement.sh that asserted the bare `adb shell getprop <key>` block had not returned to bench-kit/START-HERE.html was removed in the rewrite, leaving only .github/copilot-instructions.md, which is documentation rather than a mechanical guard. STILL OPEN AND CORRECTLY CARRIED. It is the tracker's v-offerguard and it is scheduled in docs/reference/producer-prompt-2026-09-16-batch2.md.
```

</details>

---


## 2026-09-14 — c388c2c — Repair run for WebUSB+Benchkit Integration

- [x] `tests/test-android-raw-agreement.sh:47-50` whitespace/blanks test is a tautology:
      TICKED 16 September, verified against the current file: the whitespace step perturbs with `sed 's/^/  /'` and asserts the derivation DIFFERS from canonical. Nothing strips it back. The tautology went with the c388c2c rewrite.
      adds leading spaces then strips them before asserting, so it tests
      derive.sh(x)==derive.sh(x), not whitespace tolerance; derive.sh
      actually fails on leading-whitespace input (g() requires key at
      position 1)
- [x] `tests/test-android-raw-agreement.sh:8` comment says bare-value fallback "is
      TICKED 16 September, verified: the comment at line 8 now points at tests/run-console-logic.js, which does test bare-value refusal through the shipped isValidRawProps (`bare values with no '=' are refused`, passing on every fixture). The comment and the code agree.
      refused"; lines 16–22 test only that the UI text was removed, not
      that pasting bare values is rejected

<details><summary>the review, as it came back</summary>

```

Review of c388c2c

1. What changed that was not asked for?

Nothing in the diff goes beyond the four files' stated concerns. The changes are: CRLF normalisation, ubuntu_live routing, pending-only records in saveRecord, merge.py gating, schema documentation, and test expansion. No new feature, no new screen, no scope creep.

2. What did it decide that was not already in a file?

Nothing material. The pending-only record shape, the merge.py gate, and the raw validation guard are implementations of constraints that are now documented in data/schema.md:141–146. The ubuntu_live routing change (scrPrep → scrBootUp → scrAndroidBash) is a flow decision that is not documented anywhere as a design choice — but it restores the prep screens that already existed in the code, so it is a routing repair rather than a new decision.

3. Does any test pass for a reason other than the code being correct?

Yes. The whitespace/blanks test at tests/test-android-raw-agreement.sh:47–56 is a tautology. It:

1. Takes clean key=value fixture text (line 31: bash_raw)
2. Adds leading whitespace and blank lines (line 48: awk '{print "  " $0 "\n"}')
3. Strips them back out (line 49: sed 's/^[[:space:]]*//; s/[[:space:]]*$//' | grep -v '^$')
4. Feeds the stripped text to derive.sh
5. Asserts the result matches the original

The normalised text is identical to the original input. The test proves that derive.sh(x) == derive.sh(x), which is determinism, not whitespace robustness. derive.sh cannot handle leading whitespace — its g() function uses index($0, k "=") == 1, which requires the key at position 1. A real whitespace-contaminated paste would silently return unknown for every field.

No code path in the HTML page strips leading whitespace either — the page does rawInput.replace(/\r\n?/g, "\n") and .trim(), neither of which strips per-line leading spaces. So the scenario the test claims to cover (lines 5–8 of the file) would fail in production, but the test passes because it undoes its own perturbation before asserting.

4. Does any file, name or comment describe something as existing that does not?

The test comment at tests/test-android-raw-agreement.sh:8 says it verifies that bare-value fallback "is refused". The test at lines 16–22 checks only that the bare-command UI text was removed from the HTML (a grep -q for its absence). It does not test that pasting bare values into scrAndroidRaw is rejected. The HTML validation at START-HERE.html:769 does reject bare values, so the feature exists — but the test's comment overstates what it proves.

5. Does anything here create a path to a false safe?

No. The changes are on the capture/collection side (bench kit and merge pipeline). The verifier at flashguard/verify.py is not touched. The saveRecord change at START-HERE.html:915–919 reduces what a pending record contains (only android_raw and android_derivation: "pending", no derived fields), which is strictly safer than the previous version that emitted seventeen "unknown" fields alongside the raw text — a record with no partition_scheme field cannot be mistaken for one that was examined. The merge.py gate at lines 101–103 prevents pending records from reaching the published matrix. Neither change touches the verify path.

---

FINDINGS
- [x] `tests/test-android-raw-agreement.sh:47-50` whitespace/blanks test is a tautology:
      TICKED 16 September, verified against the current file: the whitespace step perturbs with `sed 's/^/  /'` and asserts the derivation DIFFERS from canonical. Nothing strips it back. The tautology went with the c388c2c rewrite.
      adds leading spaces then strips them before asserting, so it tests
      derive.sh(x)==derive.sh(x), not whitespace tolerance; derive.sh
      actually fails on leading-whitespace input (g() requires key at
      position 1)
- [x] `tests/test-android-raw-agreement.sh:8` comment says bare-value fallback "is
      TICKED 16 September, verified: the comment at line 8 now points at tests/run-console-logic.js, which does test bare-value refusal through the shipped isValidRawProps (`bare values with no '=' are refused`, passing on every fixture). The comment and the code agree.
      refused"; lines 16–22 test only that the UI text was removed, not
      that pasting bare values is rejected
```

</details>

---


## 2026-09-14 — verification of the five carried findings — not a review

Filed by the analysing session, not by a blind reviewer. It is here because it changes the
severity of two findings and adds evidence neither read had.

**Finding 3 is worse than filed, and it is now reproduced.** The tautological test was
covering a real defect. The two step-2 routes do not differ in derivation, they differ in the
SHAPE of the text that arrives, and `adb shell` on Windows prints CRLF while the raw-paste
path only trims the ends of the blob. Run from the repository root:

```
F=tests/android/real-nothing-phone-2026-08-29.props
grep -v '^#!' $F | bash bench-kit/scripts/derive.sh | grep -E 'partition_scheme|bootloader_state'
grep -v '^#!' $F | sed 's/$/\r/' | bash bench-kit/scripts/derive.sh | grep -E 'partition_scheme|bootloader_state'
```

LF gives `virtual_A/B` and `locked`. CRLF gives `A/B` and `unknown`. The first is a DIFFERENT
CONFIDENT ANSWER on a recipe-matching field, not an abstention. The second throws away an
earned `unsafe`. This affects only the Windows path, which is the platform most testers are
expected to use, and the test written to catch exactly this could not fail.

**The documented cmd.exe fallback produces a meaningless record.** `START-HERE.html:762` tells
a tester to run nineteen bare `adb shell getprop <key>` lines, each printing a value with no
key. `cut -d= -f2- | bash bench-kit/scripts/derive.sh` returns `unknown` for every field, so
the record is shaped exactly like `tests/android/empty-everything.props`, the fixture for a
phone that answered nothing. Following the instructions produces a record indistinguishable
from a dead device.

**Finding 4 is a functional hole, not a stale comment.** `scrPlatform:690` offers the Ubuntu
stick and `scrRoutePlatform:706` routes it straight to `scrAndroidBash("linux_live")`. A
tester who picks it is told to run a bash script on a machine nobody told them how to make.

**Finding 5's severity is as the reviewer's long note stated**, and that note was right: no
false safe today because the verifier abstains on `unknown`, but seventeen fields claiming
"could not be established read-only" when they mean "not computed yet" pollutes the matrix the
first moment anything treats `unknown` as ground truth. Nothing outside START-HERE.html knows
these fields exist, which is how it stays latent.

**Finding 1 is a wording defect in the finding, not a defect in the fixture.** The fixture
contains `<stripped>`, a redaction marker, which is the evidence the masker ran on the device
that caused the fourteen-day leak. Removing it would remove the proof. Ranaji's ruling.

Repair task: `docs/reference/producer-prompt-2026-09-14-repair.md`.

---


## 2026-09-14 — d83c342 — Integration of WebUSB and Bench Kit for a tool that can be run by independent testers

- [x] tests/test-android-raw-agreement.sh:23 Route 2 sets raw_paste="$bash_raw" — the same variable Route 1 used — then pipes it through the same derive.sh. The test compares identical input through identical processing and always passes regardless of code correctness.
      TICKED 16 September, verified against the current file: test-android-raw-agreement.sh was rewritten end to end in c388c2c. Line 23 is now the canonical baseline `bash_derived=$(printf ... | bash $DERIVE)`, and `grep -n 'tr -d'` over the whole file returns nothing. Every hazard step perturbs and does NOT undo.
- [x] bench-kit/START-HERE.html:784 Comment says "Legacy Ubuntu Prep & Boot Screens (Accessible if requested)" but no calling path in the file reaches scrPrep() or scrBootUp(). The functions are dead code; the comment describes reachability that does not exist.
      TICKED 16 September, verified: the string `Legacy` does not appear anywhere in bench-kit/START-HERE.html, and `git log -S` shows c388c2c removed that comment on 14 September. The reachability claim is also false now: scrRoutePlatform reaches scrPrep, and scrPrep reaches scrBootUp.
- [x] bench-kit/START-HERE.html:914 android_raw and android_derivation are not in the schema (data/schema.md). The raw-paste path writes an undocumented field to the record and marks 17 Android fields as "unknown" meaning "not yet derived", conflating it with "unknown" meaning "could not be established read-only" — the exact ambiguity schema version 0.2 was redesigned to eliminate.
      TICKED 16 September. Fixed in batch 1: data/schema.md documents android_raw and android_derivation as a distinct uncomputed state, buildAndroidBlock emits exactly those two keys for a raw capture, data/merge.py refuses a pending record, and tests/test_contributions_validation.py fails when that refusal is removed (verified by planting `if False:`).

<details><summary>the review, as it came back</summary>

```
Review of d83c342

1. What changed that was not asked for?

The commit title says "Integrate WebUSB step 1 and multi-platform step 2 into START-HERE.html". Beyond that integration:

- tests/webusb-probe.html received a four-line SUPERSEDED notice (lines 1–4). This is commentary on a file the diff does not modify substantively and was not part of the stated scope, though it is harmless.
- The legacy Ubuntu screens (scrPrep, scrBootUp) were gutted to stubs (lines 784–807). The diff removed detailed preparation and boot guides that existed in v3 and replaced them with skeleton cards. No calling path reaches them (covered under Q4), so this is dead code added rather than retained. It could have been removed entirely; leaving it creates the appearance of functionality that does not exist.

2. What did it decide that was not already in a file?

- capture_route defaults to "browser" on every new capture (bench-kit/START-HERE.html:437). The schema doc (data/schema.md:152–153) says capture_route was added to distinguish what the shipped tool can do from what linux_live can do, and warns "absence is not a value; an unrecorded capture must not be assumed to have used any particular route." The HTML picks "browser" as the default before knowing whether WebUSB succeeded, whether the user skipped it, or whether the tester went through the bash path. The bash path later overwrites it to "adb_host" (line 776), and the raw-paste path sets "adb_host" too — so the default only survives for non-phone devices that go through scrWebUSB and reach scrConfirm. That default itself is reasonable (WebUSB is the browser route), but the decision to make "browser" the fallback rather than "not_stated" or a sentinel for "undetermined" was made in this commit, not derived from any prior document.
- android_derivation: "pending" as a record field (line 915). The raw-paste path stores the tester's pasted text as android_raw and marks derivation as "pending", meaning the record is written with all Android fields set to "unknown" and derivation deferred. No document I was told to read specifies this deferred-derivation pattern. The schema (data/schema.md) has no android_raw or android_derivation field. The record will be written to device-matrix.jsonl with an undocumented field and a batch of "unknown" values that mean "not yet derived" rather than "could not be established read-only" — conflating two of the three-way absence semantics the schema was specifically redesigned to distinguish (schema.md lines 37–43).

3. Does any test pass for a reason other than the code being correct?

Yes. tests/test-android-raw-agreement.sh is a tautology.

The test claims to assert that "the bash path (02-android.sh) and the raw-paste path produce the same derived fields when derive.sh runs over the raw property text."

Lines 18–24:

# Route 1: Simulated bash path (derived directly)
bash_raw=$(grep -v '^#!' "$f")
bash_derived=$(printf '%s\n' "$bash_raw" | bash "$DERIVE")

# Route 2: Simulated raw paste path (verbatim raw text, derived via derive.sh)
raw_paste="$bash_raw"
raw_derived=$(printf '%s\n' "$raw_paste" | bash "$DERIVE")

Route 2 sets raw_paste="$bash_raw" — the identical variable from Route 1 — and pipes it through the identical command (bash "$DERIVE"). The comparison at line 26 ("$bash_derived" = "$raw_derived") compares two runs of the same function on the same input. It will always pass.

The test the name promises — that the raw-paste path in START-HERE.html and the bash path through 02-android.sh produce the same record — would require either (a) actually exercising the raw-paste parsing code to produce key=value lines, or (b) at minimum, transforming the fixture text differently for each route. As written, Route 2 is Route 1 copy-pasted with a different variable name.

This test is wired into tests/all.sh (the line echo "  ANDROID RAW AGREEMENT"; bash "$HERE/test-android-raw-agreement.sh" || exit 1), so it runs in the build and reports "ok" across all fixtures, giving the appearance of coverage where none exists.

4. Does any file, name or comment describe something as existing that does not?

Yes. bench-kit/START-HERE.html:784:

/* ---------- Legacy Ubuntu Prep & Boot Screens (Accessible if requested) ---------- */

scrPrep() and scrBootUp() are defined at lines 785–807. The comment says they are "Accessible if requested." They are not accessible: no button, no event handler, and no initialization code in the file calls either function. The v3 flow that reached them (the location chooser scrBoot, then the setup script step scrSetup) was removed in this diff. The functions are dead code, and the comment claims they are reachable.

5. Does anything here create a path to a false safe?

Not directly. The else if (cur.dev.expect) devClass = cur.dev.expect; fallback at line 639 echoes the tester's category selection as the detected device class when no interface-level match fires, which means a misidentified device category could propagate to the record as device_class. But device_class on the record flows into the device matrix, not into the verifier's verdict path — the verifier takes a fingerprint and a recipe as input, not a bench-console device class. This fallback affects data quality, but it does not create a code path where verify.py returns safe when it should not.

The android_raw / android_derivation: "pending" pattern (lines 912–923) writes every Android field as "unknown", which the verifier should treat as an abstention signal. As long as the verifier continues to abstain on unknown fields — which it does; the build fails on a false safe, and the suite output confirms the false-safe gate is armed — this does not produce a false safe. But it is worth noting that a record carrying 17 "unknown" Android fields is not the same as a record with "unknown" because the device did not expose the properties: the former will be derived later, the latter is final. If a future merge.py or coverage.py change treats every "unknown" as ground truth, these deferred-derivation records would silently pollute the matrix.

---

FINDINGS

- [x] tests/test-android-raw-agreement.sh:23 Route 2 sets raw_paste="$bash_raw" — the same variable Route 1 used — then pipes it through the same derive.sh. The test compares identical input through identical processing and always passes regardless of code correctness.
      TICKED 16 September, verified against the current file: test-android-raw-agreement.sh was rewritten end to end in c388c2c. Line 23 is now the canonical baseline `bash_derived=$(printf ... | bash $DERIVE)`, and `grep -n 'tr -d'` over the whole file returns nothing. Every hazard step perturbs and does NOT undo.
- [x] bench-kit/START-HERE.html:784 Comment says "Legacy Ubuntu Prep & Boot Screens (Accessible if requested)" but no calling path in the file reaches scrPrep() or scrBootUp(). The functions are dead code; the comment describes reachability that does not exist.
      TICKED 16 September, verified: the string `Legacy` does not appear anywhere in bench-kit/START-HERE.html, and `git log -S` shows c388c2c removed that comment on 14 September. The reachability claim is also false now: scrRoutePlatform reaches scrPrep, and scrPrep reaches scrBootUp.
- [x] bench-kit/START-HERE.html:914 android_raw and android_derivation are not in the schema (data/schema.md). The raw-paste path writes an undocumented field to the record and marks 17 Android fields as "unknown" meaning "not yet derived", conflating it with "unknown" meaning "could not be established read-only" — the exact ambiguity schema version 0.2 was redesigned to eliminate.
      TICKED 16 September. Fixed in batch 1: data/schema.md documents android_raw and android_derivation as a distinct uncomputed state, buildAndroidBlock emits exactly those two keys for a raw capture, data/merge.py refuses a pending record, and tests/test_contributions_validation.py fails when that refusal is removed (verified by planting `if False:`).
```

</details>

---


## 2026-09-13 — edb6008 — Restoring missed findings

- [x] tests/webusb-fixtures/18d1-4ee2.desc:10 stores a device serial number (_SN:<stripped>)
      TICKED 16 September, ruled 14 September and never recorded here, which is why it came back five times. The fixture contains `<stripped>`, the redaction MARKER, not a serial -- the finding quotes the marker in its own text. It is the evidence the masker ran on the device that caused the fourteen-day leak, and removing it would remove the proof.
      in the product field, violating the strict data rule against recording serials.
- [x] tests/webusb-probe.html:94 removes the protective comment explaining why **Fixed and confirmed by the second read, 14 Sep: the comment is restored at lines 96-103 with the masker beside it.**
      serial numbers are not read or printed, an unasked-for change that enabled the leak above.

<details><summary>the review, as it came back</summary>

```
1. What changed that was not asked for?
N/A
2. What did it decide that was not already in a file?
N/A
3. Does any test pass for a reason other than the code being correct?
N/A
4. Does any file, name or comment describe something as existing that does not?
N/A
5. Does anything here create a path to a false safe?
N/A

  FINDINGS
  - [x] tests/webusb-fixtures/18d1-4ee2.desc:10 stores a device serial number (_SN:<stripped>)
      TICKED 16 September, ruled 14 September and never recorded here, which is why it came back five times. The fixture contains `<stripped>`, the redaction MARKER, not a serial -- the finding quotes the marker in its own text. It is the evidence the masker ran on the device that caused the fourteen-day leak, and removing it would remove the proof.
        in the product field, violating the strict data rule against recording serials.
  - [ ] tests/webusb-probe.html:94 removes the protective comment explaining why
        serial numbers are not read or printed, an unasked-for change that enabled the leak above.
```

</details>

---


## 2026-09-13 — b73c93f — Variant Grading and v0.2 tests

- [x] `docs/reasoning/safe-case.md:39`
      AUTHORISED, and the reviewer could not have known. Both decisions were made by Ranaji on
      12 Sep and relayed in the task; the resolution in safe-case.md matches them word for word.
      The packet deliberately excludes the task, so a blind reviewer flags every authorised
      decision as unauthorised. That is a permanent cost of blindness, not a defect, and it is
      cheaper than the alternative. Noted here so the next one is recognised quickly.
- [x] `flashguard/verify.py:282`
      REAL, AND BIGGER THAN IT LOOKED. identity_source is not invented: it is a schema field
      carried by 8 of the 10 records in the matrix, set whenever a tester names the DEVICE. Read
      as variant confirmation, almost every real record would have confirmed its own variant
      with no human involved. variant_source and human_confirmed were genuinely invented.
      Fixed: one field, variant_confirmed_by, defined in data/schema.md, absence means no
      confirmation. Test added asserting tester_identified does NOT confirm a variant.
- [x] `docs/reasoning/verdict-contract.md:75`
      REAL. The contract listed four prerequisite fields; the verifier reads the key and
      `required` only. Fixed in the contract rather than the code: declared_by and
      source_evidence are provenance and legitimately unread, but a contract that lists four
      fields without distinguishing them implies all four participate. `state` is carried and
      unread on every recipe and should be dropped if it stays that way.
- [x] `tests/test_verify_v2.py:131`
      REAL. Fixed in cf1b009: a test that enters the dangerous branch now exists and fails on
      the old code.
- [x] `flashguard/verify.py:276`
      REAL, AND IT WAS A SHIPPED FALSE SAFE. Reproduced against the FP3 recipe before changing
      anything: alias device code, unknown variant, prerequisite satisfied, verdict safe, zero
      variant reasons, and fields_consumed still claiming the variant. Fixed in cf1b009: an
      unconfirmed variant always abstains, and whether supported_device_codes is a variant- or
      family-level claim is now DISPUTED rather than decided by a branch.

<details><summary>the review, as it came back</summary>

```
1. What changed that was not asked for?
   The assistant resolved the two DISPUTED blocks regarding variant matching and the evidence expiry boundary (around docs/reasoning/safe-case.md:39). It decided them itself and removed the markers, despite those markers explicitly stating that no test could settle them and that they "need a decision from Ranaji".
2. What did it decide that was not already in a file?
   It decided on specific fingerprint keys (variant_source, identity_source, human_confirmed) and strings ("human", "tester_identified", "human_confirmed") to evaluate whether a variant was human-confirmed (flashguard/verify.py:282). These mapping decisions and keys were invented in this commit and were not defined in the contract or any other file prior.
3. Does any test pass for a reason other than the code being correct?
   Yes. In tests/test_verify_v2.py:131, test_unconfirmed_variant_with_agreeing_partition_and_bootloader_abstains_naming_variant asserts that an unconfirmed variant results in a cannot-verify verdict. This test only passes because BASE_RECIPE leaves supported_device_codes empty. Because of a bug in the code, if product_device matched an alias, it would wrongly skip the abstain altogether.
4. Does any file, name or comment describe something as existing that does not?
   Yes. docs/reasoning/verdict-contract.md:75 describes prerequisites as carrying state, declared_by, and source_evidence. However, the verification code (flashguard/verify.py:336-339) ignores all of these fields entirely and only retrieves the required field, making the contract's description of the structure an unfulfilled claim.
5. Does anything here create a path to a fals
   Yes. At flashguard/verify.py:276, if a recipe requires a variant but the fingerprint does not provide one (it is unconfirmed), the code explicitly passes—s-variant abstain reason—if the observed_device happens to match a supported_device_codes alias. This directly violates the contract (which states an unconfirmed
   variant must return cannot-verify and NEVEr path to a false safe.

  FINDINGS
- [x] `docs/reasoning/safe-case.md:39`
      AUTHORISED, and the reviewer could not have known. Both decisions were made by Ranaji on
      12 Sep and relayed in the task; the resolution in safe-case.md matches them word for word.
      The packet deliberately excludes the task, so a blind reviewer flags every authorised
      decision as unauthorised. That is a permanent cost of blindness, not a defect, and it is
      cheaper than the alternative. Noted here so the next one is recognised quickly.
- [x] `flashguard/verify.py:282`
      REAL, AND BIGGER THAN IT LOOKED. identity_source is not invented: it is a schema field
      carried by 8 of the 10 records in the matrix, set whenever a tester names the DEVICE. Read
      as variant confirmation, almost every real record would have confirmed its own variant
      with no human involved. variant_source and human_confirmed were genuinely invented.
      Fixed: one field, variant_confirmed_by, defined in data/schema.md, absence means no
      confirmation. Test added asserting tester_identified does NOT confirm a variant.
- [x] `docs/reasoning/verdict-contract.md:75`
      REAL. The contract listed four prerequisite fields; the verifier reads the key and
      `required` only. Fixed in the contract rather than the code: declared_by and
      source_evidence are provenance and legitimately unread, but a contract that lists four
      fields without distinguishing them implies all four participate. `state` is carried and
      unread on every recipe and should be dropped if it stays that way.
- [x] `tests/test_verify_v2.py:131`
      REAL. Fixed in cf1b009: a test that enters the dangerous branch now exists and fails on
      the old code.
- [x] `flashguard/verify.py:276`
      REAL, AND IT WAS A SHIPPED FALSE SAFE. Reproduced against the FP3 recipe before changing
      anything: alias device code, unknown variant, prerequisite satisfied, verdict safe, zero
      variant reasons, and fields_consumed still claiming the variant. Fixed in cf1b009: an
      unconfirmed variant always abstains, and whether supported_device_codes is a variant- or
      family-level claim is now DISPUTED rather than decided by a branch.
```

</details>

---


## 2026-09-08 — 0e2041d — double checking before verifier build

- [x] `tests/review-log-add.sh:43` decided whether a review covered uncommitted
      work by matching the substring "uncommitted" inside a human sentence, so an
      explicit BASE like `fix-uncommitted-bug` would have filed committed work as
      uncommitted. Fixed in c85da82: the packet writes a MODE token as its own
      field, so nothing has to infer the mode from prose.
      (This finding also arrived truncated, the second in a row. cad6129 now
      catches a line number running into mid-word text, which is that
      failure's signature.)

<details><summary>the review, as it came back</summary>

```
Good. Now I have what I need to answer the five questions about commit 0e2041d.

---

1. What changed that was not asked for?

The two trailing-newline additions in data/recipe_format_coverage.py:119 and docs/reasoning/recipe-format-coverage.md:143 are cosmetic whitespace fixes — not substantive, not harmful, and not on any verification path. Whether they were asked for is unknowable from the diff; either way, they change nothing that matters.

The remaining three files — docs/reference/review-log.md, tests/review-log-add.sh, and tests/review-packet.sh — all address one thing: the filing process was stamping reviews against the wrong commit. That is a single fix across three files. Nothing in the diff introduces a feature, a concept, or a capability beyond correcting the logging plumbing.

2. What did it decide that was
                                                                                          One decision is made: review-paence file(.git/review-packet-ref) and review-log-add.sh reads it to determine the SHA for the      heading. This decision is documsts/review-packet.sh:38–43 andtests/review-log-add.sh:36–38, and the VOID header in docs/reference/review-log.md:56–63  records why.
                                                                                          The pipe-delimited format (WHERreview-packet.sh:44 is notdocumented anywhere as a contract — it exists only implicitly, coupled between the printf at line 44 and the cut at testss is fine for two scripts in thesame directory, but it is a decision that lives only in code, not in prose.               
3. Does any test pass for a reason other than the code being correct?                     
The new logic has a fallback: when no review-packet-ref file exists, review-log-add.sh:48 falls back to $(git log -1 --foing. This means the old behaviour is preserved as a degraded path — existing tests that never build a packet first still work. That is correct rather th tells the user the heading mayname the wrong thing.

The case match at review-log-add.sh:43–46 tests $W for *uncommitted*. The packet writes
WHERE as the first field (tests WHERE is set to "uncommittedwork in the tree" at line 33. The glob *uncommitted* matches this. However, it would also
match any explicit BASE argumento contain the substring"uncommitted" — e.g., a branch named fix-uncommitted-bug would produce WHERE="explicit
range fix-uncommitted-bug..HEADted*, and the SHA would bewritten as uncommitted-on-<hash> when it should not be. This is not a test-correctness
issue per se, but it is a fragi

4. Does any file, name or commexisting that does not?

The VOID entry at docs/referenc

▎ Fixed: review-packet.sh now wgit/review-packet-ref, andreview-log-add.sh files against that rather than assuming HEAD.

This describes the fix as already done, and the code confirms it does exist (review-packet.sh:44–45, reviewstale descriptions found.

5. Does anything here create a

No. None of these files are on ipe_format_coverage.py is ameasurement script. recipe-format-coverage.md is a reasoning document. The three
review-tooling files are test iand label reviews. Nothing inthis diff touches flashguard/verify.py, the verdict contract, any recipe, or any schema.

---

FINDINGS
- [ ] tests/review-log-add.sh:4atches on substring, so a branch
  name or explicit BASE containing "uncommitted" (e.g. fix-uncommitted-bug) would
  produce a uncommitted-on- SHAreviewed committed work
```

</details>

---


## 2026-09-08 — 999ad74 — before the verifier build

**VOID. This did not review 999ad74.** The packet was built while two trailing-newline
edits were uncommitted, so it diffed those two characters and nothing else, and the filer
stamped it with the last commit hash. The 269-line coverage measurement in 999ad74 has
never been reviewed. Kept rather than deleted, because a log that quietly loses its own
mistakes is not a record.

Fixed: `review-packet.sh` now writes what it covered to `.git/review-packet-ref`, and
`review-log-add.sh` files against that rather than assuming HEAD.

Nothing found. Recorded because a log of only non-empty reviews is a biased log, and because "has this been reviewed at all" is a question worth being able to answer.

<details><summary>the review, as it came back</summary>

```
The diff is clear: both files had their final line missing a trailing newline, and the only change is adding that trailing newline. Let me confirm there's nothing else by checking what the review packet's "1 OPEN DISAGREEMENT" and "PLACEHOLDERS" refer to, since those are suite outputs not part of my review scope.

The diff is two files, each with a single-character change: a missing newline at end-of-file is added. That's the entire content.

1. What changed that was not asked for?

Nothing substantive changed. Both edits add a trailing newline to the final line of the file — data/recipe_format_coverage.py:119 and docs/reasoning/recipe-format-coverage.md:143. No logic, no prose, no data was altered. Whether this was asked for or not, it changes nothing that matters.

2. What did it decide that was not already in a file?

Nothing. No decision is expressed in either edit.

3. Does any test pass for a reaing correct?

Not from this diff. The change ng newline). It cannot affecttest outcomes in either direction.

4. Does any file, name or comment describe something as existing that does not?

No. The content of both files is unchanged except for the newline character.

5. Does anything here create a path to a false safe?

No. Neither file is on the verification path. recipe_format_coverage.py is a measurement
script; recipe-format-coverage.. Neither touchesflashguard/verify.py or any verdict logic.

---

FINDINGS
none
```

</details>

---


## 2026-09-07 — 047af5a — recipes indeed have prerequisites

- [x] `tests/tracker-export.py:60` the `fingerprint()` docstring still said the hash
      covers "the lengths of the body and note" while the code hashes the content. It
      described the behaviour this commit removed. Fixed 7 Sep.

**This entry arrived corrupted, and that is worth keeping rather than tidying away.** The
stored answer below is missing runs of characters ("or commexisting that does not", "a
versiohe project tracker"), and the finding line was unreadable as filed. The clipboard was
copied while the CLI was still rendering, so `pbpaste` took a partly-written buffer. The
finding itself was correct and has been rewritten above from the readable fragments.
`tests/review-log-add.sh` now refuses input that looks truncated, because a finding nobody
can read is carried forward for ever and can never be honestly ticked.

<details><summary>the review, as it came back</summary>

```
Here is my review.

Answers

1. What changed that was not asked for?

Nothing. Both files contain the same change: the fingerprint string now includes the full body and note content instead of their lengths, and the hash iterates UTF-16 code units instead of Python ord() on characters. The JS page (not version-controlled) already carries the matching update. The scope is tight.

2. What did it decide that was not already in a file?

Nothing new was decided. The fingerprint's purpose (detect drift between file and published page) and the hash algorithm (djb2) are unchanged. The implementation was corrected, not redesigned.

3. Does any test pass for a reason other than the code being correct?

No. check-tracker.sh computes the fingerprint independently from tracker-export.py (one parses the HTML inline, the other is a standalone script), and both must agree with the JavaScript page for the version banner to match. The hash is computed against real tracker data, not a stub.

4. Does any file, name or commexisting that does not?

Yes. tests/tracker-export.py:60cstring says the hash covers "the lengths of the body and note". The code on lines 68–69 now hashes the bodies themselves.
The docstring describes the oldat this commit replaced.

5. Does anything here create a

No. The fingerprint is a versiohe project tracker. It has noconnection to flashguard/verify.py or the verdict logic.

---

FINDINGS
- [ ] tests/tracker-export.py:6ths of the body and note" but the
  code now hashes the full content, not lengths; it describes the pre-fix behavior
  that this commit removed
```

</details>

---


## 2026-09-07 — 474df9e — the workflow doc reporting itself as a disagreement

Reviewed blind by the CLI, first real use of this workflow. It answered all five questions,
cited lines, and found nothing. Verified independently: the commit is one line in one file
and every description it gave is accurate. An empty review is recorded because a log of only
non-empty reviews is a biased log.

Two things a second pass found that the review did not.

- [x] The review quoted the commit message, which is **not in the packet** — `git diff`
      and `git diff --stat` carry no message and the header prints only the hash. It had a
      shell, ran `git log`, and read the producer's account of the change before answering
      question 1, which asks what changed that was *not* asked for.
      Fixed: the packet now tells the reviewer not to read the commit message, the log, or
      any file explaining why, and `docs/reference/review-workflow.md` says to notice it when
      a review quotes one.
- [x] `tests/check-disputed.sh:22` the commit under review fixed the **document** to get
      past the grep, rather than the grep. The pattern matched the bare word anywhere on any
      line, and already carried two filenames excluded by substring — invisible exemptions,
      the same shape as the publication scan that exempted the only file that could fail it.
      The next document to explain the convention would have hit it again.
      Fixed: a marker is now a line whose first non-space characters are a comment opener and
      then the word. The two skipped paths are skipped by path, for a stated reason, and the
      skip is printed. `review-workflow.md` has its accurate wording back.

Neither is a criticism of the review. The first is the packet's fault and is now the packet's
fix. The second is the kind of thing a blind reviewer is least placed to see, because it
requires asking whether the change was the right shape rather than whether it was correct —
and the commit message it had already read said the change was a fix.

---

*Older reviews go below. Newest at the top.*
