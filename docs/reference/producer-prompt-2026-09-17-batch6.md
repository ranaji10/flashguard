# Batch 6 — the fourth false safe, and the field name no device produces

Two defects, both reproduced against the working tree on 16 September. Section 1 is a **live
false safe** and must land before anything in this batch is committed. Section 2 is what lets
the coverage gate see section 1 at all.

Do not refactor beyond what each section asks for. Do not change any file this prompt does not
name. Every section ends with a command whose output must be pasted back.

---

## 1. `avicii.json` returns `safe` against its own declared verdict

### Reproduce it first

```
python3 - <<'EOF'
import json, sys; sys.path.insert(0,'.')
from flashguard.verify import verify
r=json.load(open('data/recipes-v0.2/avicii.json')); t=r['target']
fp={"product_device":t['product_device'],"product_model":t['models'][0],
    "partition_scheme":t.get('partition_scheme'),"bootloader_unlocked":"unlocked",
    "android_version":12}
print(r['expected_verdict'], r['human_assessment'], '->', verify(fp,r)['verdict'])
EOF
```

Expected today: `cannot-verify unsafe -> safe`. If it does not print that, stop and say so.

### Why it happens

`flashguard/verify.py:417` builds `has_unlock_operation` by looking for an `operations` entry
whose `kind` is `unlock_bootloader` or `unlock`. `avicii.json` has an empty `operations` list
and declares its unlock as `prerequisites.bootloader_unlocked.declared_by = "unlock_bootloader"`.
So the guard never fires, `is_unlock` is false for that prerequisite, and the unlock condition
is checked as a plain equality that the fingerprint satisfies.

This is the third time the same shape has produced a false safe in this repository: **a gate
that allowlists what triggers it.** The rule is the one already written into the untested gate
and the unlock-class gate — *the safe direction must be the narrow one.*

### What to change

In `flashguard/verify.py`, a prerequisite is an unlock step if **any** of these hold:

- it carries `unlock_step: true`
- it carries `unlock_class`
- its `declared_by` value contains `unlock`
- its name appears in the schema's unlock-condition mapping (section 2 adds that mapping; until
  it exists, treat `bootloader_unlocked` and `bootloader_state` as unlock condition names)

And invert the guard. Today the recipe must prove an unlock is involved before the check
applies. Reverse it: **if any prerequisite is an unlock step and none of them carries an
`unlock_class`, abstain** with `unlock-class-undeclared`, naming the prerequisite. A recipe that
genuinely involves no unlock states `operations: []` *and* carries no unlock-shaped prerequisite,
and is unaffected.

Remove the `is_unlock_step` alias. It appears in no recipe, no schema entry, no test and no
document, and a second name for one thing is the problem this project keeps re-finding.

### Also in this section: the untested gate has a type hole

`flashguard/verify.py:511` permits when `upstream_untested` is `in (False, "unestablished", None)`.
In Python `0 == False`, so `0` and `0.0` permit. Compare by identity: `is False`, `is None`, or
an exact string match. Verify:

```
python3 - <<'EOF'
import json,copy,sys; sys.path.insert(0,'.')
from flashguard.verify import verify
r=json.load(open('data/recipes-v0.2/avicii.json')); t=r['target']
fp={"product_device":t['product_device'],"product_model":t['models'][0],
    "partition_scheme":t.get('partition_scheme'),"bootloader_unlocked":"unlocked","android_version":12}
for v in [0, 0.0, False, "unestablished", 1, True]:
    r2=copy.deepcopy(r); r2['source']['upstream_untested']=v
    print(repr(v), '->', verify(fp,r2)['verdict'])
EOF
```

After the fix, `0` and `0.0` must not reach `safe`. `False` and `"unestablished"` must still
permit. `1` must not permit.

### And one documentation disagreement found in the same review

`docs/reasoning/verdict-contract.md:157` documents `"not_untested"` as a permitted value with no
effect. The verifier returns `cannot-verify` with `recipe-untested-unrecognized` for it. The
**code is right** — it is outside the vocabulary. Delete the line from the document rather than
widening the gate.

### Tests this section must add

1. `avicii.json` as a fixture in the false-safe test, asserting the verdict is not `safe` while
   its `human_assessment` is `unsafe`. Not a hand-built recipe — **the file on disk**, so this
   exact regression fails the build.
2. A test asserting `source.upstream_untested = 0` does not reach `safe`.
3. A test asserting a prerequisite whose `declared_by` names an unlock is treated as an unlock
   step even with no `operations` entry.

### Paste back

```
python3 -m pytest tests/ -q 2>&1 | tail -5
python3 data/coverage.py | sed -n '1,12p;/VERIFIER GATE/,$p'
```

---

## 2. Every recipe asks for a field no capture route produces

### The facts, all checked

- All six recipes in `data/recipes-v0.2/` name their unlock prerequisite `bootloader_unlocked`.
- All ten records in `data/device-matrix.jsonl` carry `detected.android.bootloader_state`.
- **None carries `bootloader_unlocked`.**
- `bench-kit/scripts/derive.sh` emits `bootloader_state`; `tests/run-android.sh` maps
  `bootloader:bootloader_state`.
- `tests/test_verify_v2.py` takes a fixture parameter named `bootloader_state` and assigns it
  into a field named `bootloader_unlocked`, which is what hid this behind seventeen passing tests.

### What to change

**a. The recipes.** Key the unlock prerequisite on `bootloader_state` in all six files, required
value `unlocked`. Keep everything else on those prerequisites as it is.

**b. The fixture.** In `tests/test_verify_v2.py`, stop renaming the field. The fixture writes
`bootloader_state`, because that is what a capture produces. Expect tests to fail; fix them by
correcting the field name, never by reintroducing the alias.

**c. The mapping, which is the actual fix.** Add to `data/schema.md` a declared mapping from
prerequisite condition to the fingerprint field that carries its evidence — starting with
`bootloader_unlocked → bootloader_state`. State in one line why it exists: *a recipe may only ask
for evidence some capture route produces.*

**d. The check.** A test that fails the build when a recipe names a prerequisite whose evidence
field appears in no capture route. Read the fields the capture route can emit from
`bench-kit/scripts/derive.sh` and `data/schema.md` rather than from a hard-coded list, and give
the failure a message that names the recipe, the prerequisite and the field nothing produces.

### The result to expect, and it is the point of the batch

```
python3 - <<'EOF'
import json, sys; sys.path.insert(0,'.')
from flashguard.verify import verify
r=json.load(open('data/recipes-v0.2/spacewar.json'))
fp={"product_device":"Spacewar","product_model":"A063",
    "partition_scheme":"virtual_A/B","bootloader_state":"locked"}
out=verify(fp,r); print(out['verdict'])
print([(x['code'], x['result']) for x in out['reasons']])
EOF
```

This must print `unsafe`, with a failing reason naming the bootloader prerequisite. That is the
first decided verdict this project has produced against a real captured device, and
`data/coverage.py` should then report **1 decided** with false safes still **0**.

### Paste back

```
python3 -m pytest tests/ -q 2>&1 | tail -5
python3 data/coverage.py | sed -n '1,20p;/VERIFIER GATE/,$p'
bash tests/check-public-safe.sh; echo "RC=$?"
git --no-optional-locks status --porcelain
```

---

## 3. Do not do

- Do not change `data/device-matrix.jsonl`. It is captured evidence.
- Do not add a compatibility alias so that both field names work. Two names for one thing is the
  defect, not the fix.
- Do not touch `docs/tracker/` or anything under `library/`.
- Do not widen any gate to make a test pass. If a test and a gate disagree, say which and stop.
