# Batch 1 of 5, 16 September. Three defects in `bench-kit/START-HERE.html`.

*Amended 16 September after research task 3. Defect 3 is new, and it is the same rule as defect 2 in the branch nobody looked at. It matters more than it did yesterday: `product_model` is about to become the field that decides whether a recipe may be applied to a device at all.*

Both block Ranaji's own test run on a new machine, so do these before anything else.
Both are in one file. Do not touch the verifier, the schema or the recipes in this batch.

Read each reproduction before writing code. They are click sequences and file lines, not
opinions. Change nothing outside the three fixes named here.

---

## 1. BLOCKING. Choosing a platform once locks the tester into it for the whole session.

`S.host_platform` is session state, saved to `localStorage` under `bench.v4` and set the
instant a platform button is pressed:

```
START-HERE.html:696    S.host_platform = p;  save();  scrRoutePlatform(p);
```

`scrPlatform()` is called from exactly one place in the file:

```
START-HERE.html:613    if(S.host_platform && S.host_platform !== "not_stated") scrRoutePlatform(S.host_platform);
START-HERE.html:614    else scrPlatform();
```

So the platform question is asked **once per session and never again**. Nothing clears the
field, and no screen downstream of it offers a way back to it.

Reproduce, by clicking:

1. Start a session, pick any phone, complete the WebUSB read.
2. At "Which operating system are you on?", press **Live Ubuntu USB stick**.
3. On the stick-preparation screen, press **Back to devices**.
4. Pick any phone again and complete the WebUSB read.

What happens: you land straight back on the Ubuntu stick-preparation screen. There is no
platform question, and no button anywhere returns you to it. The only escape is the
**Start over** button, which clears every record captured so far.

**It is not only a trap, it writes a false field.** Every record built from then on carries

```
START-HERE.html:972    host_platform: S.host_platform || "not_stated",
START-HERE.html:978    os: S.host_platform || "not_stated",
```

so a session that mis-clicked Ubuntu and then captured devices by any other means labels
every one of those records `ubuntu_live`. `host_platform` exists precisely so that a record
captured by a route the shipped product will not have can be told apart from one that can.
A wrong value in it is worse than no value.

**Fix, three parts, all small:**

1. **Do not commit the platform until the route is actually entered.** In `scrPlatform`,
   route on a local variable and set `S.host_platform` at the point each route is genuinely
   under way: `scrAndroidRaw` and `scrAndroidBash` already know their route, and
   `scrBootUp` already does this at line 825. Pressing a platform button and backing out
   must leave `S.host_platform` exactly as it was.
2. **Give every screen reachable from the platform picker a way back to it.** Add a
   `Change platform` ghost button to `scrPrep`, `scrBootUp`, `scrAndroidRaw` and
   `scrAndroidBash`, calling `scrPlatform()`. Keep the existing `Back to devices` where it
   is; this is an additional control, not a replacement.
3. **Keep the remembered platform as a default rather than a lock.** Line 613 may keep
   skipping the question for a tester who has already answered it, but `scrPlatform` must
   now show which platform is remembered and let it be changed. A one-line
   `<p class="sub">Currently set to X. Press another to change it.</p>` is enough.

**Prove it:** after the fix, repeat the four click steps above and confirm step 4 reaches the
platform question again. Then complete one capture on a non-Ubuntu route after visiting the
Ubuntu screen, export the session, and confirm `host_platform` on that record is the route
actually used.

---

## 2. BLOCKING. A pending record claims seventeen things it has not established.

The raw-paste path stores the pasted text and marks the derivation as not yet run:

```
START-HERE.html:794    cur.android_raw = t.trim();
START-HERE.html:795    cur.android_derivation = "pending";
```

and the record builder then writes both of those **alongside a full set of derived fields**,
every one of them `"unknown"`:

```
START-HERE.html:932-935   if(cur.android_raw){ ... android_raw: ..., android_derivation: "pending" }
START-HERE.html:955-965   build_fingerprint / partition_scheme / bootloader_state / ... = "unknown"
```

`data/schema.md` is explicit that `unknown` means **the field applies and could not be
established read-only**. That is a final answer about hardware. These fields mean
"not computed yet". The record cannot tell the two apart, which is exactly the three-way
absence ambiguity the schema was redesigned to prevent, reintroduced in the newest code.

There is no false safe today, because the verifier abstains on `unknown` either way. It
pollutes the matrix the first moment anything treats `unknown` as ground truth, and nothing
outside this file knows these two fields exist, which is how it stays latent.

**Fix, three parts:**

1. **When `android_derivation` is `"pending"`, emit `android_raw` and `android_derivation`
   and omit every derived key entirely.** A missing key is not a value; a wrong one is. Do
   not write `"pending"` into the derived fields either, because that invents a fourth
   absence meaning.
2. **Document both fields in `data/schema.md`**, next to the existing absence rules:
   `android_raw` is verbatim captured text awaiting derivation, and `android_derivation` is
   one of `pending` or `derived`. State that a record with `android_derivation: pending`
   carries no derived Android fields at all, and that this is not the same as `unknown`.
3. **Refuse a pending record at the matrix boundary.** Whatever validates
   `data/contributions/*.jsonl` must fail on a record whose `android_derivation` is
   `pending`, with a message saying the derivation has not been run. Add the test.

**Prove it:** produce one pending record through the paste path, export it, and confirm the
derived keys are absent rather than `"unknown"`. Then feed that exported record to the
contributions validator and confirm it is refused with the new message. Then remove the
refusal and confirm the test fails. A gate with no test proving it fires is a comment.

---

## 3. BLOCKING. A browser-only record says an Android phone has no model number.

Same rule as defect 2, in the sibling branch of the same function. `saveRecord` builds
`androidObj` three ways, and the third one is wrong.

```
START-HERE.html:924   function NA(v){ return (v===undefined||v===null||v==="")?"not_applicable":v; }
START-HERE.html:953   } else {
START-HERE.html:955     product_model:"not_applicable", product_device:"not_applicable",
START-HERE.html:956     manufacturer:"not_applicable", board_platform:"not_applicable",
...
START-HERE.html:961     partition_scheme: cur.dev.phone ? "unknown" : "not_applicable",
START-HERE.html:963     bootloader_state: cur.dev.phone ? "unknown" : "not_applicable",
```

Two fields ask whether the device is a phone. **Seventeen do not.** So a phone captured in the
browser and never taken through step 2 produces a record asserting that it has no model number,
no device codename, no manufacturer and no Android version, because `not_applicable` means in
`data/schema.md` that **the field cannot apply**. On an Android phone every one of them applies
and simply was not read. The right value is `unknown`.

The rule is already written down in this project, in the tracker item for this very file: a
browser-only Android record must write `partition_scheme` as `unknown`, never `not_applicable`.
It was applied to two fields out of nineteen.

**And `NA()` has the same fault, live on one field today.** `derive.sh` returns the string
`unknown` for what it cannot establish, so most fields pass through correctly. It returns
**empty** for `slot_suffix` on a device that exposes none. Reproduce:

```
grep -v '^#!' tests/android/empty-everything.props | bash bench-kit/scripts/derive.sh | grep slot_suffix
```

That empty value reaches `NA("")`, which returns `not_applicable` — the record then claims an
Android phone cannot have a slot suffix, when the honest answer is that it did not report one.

**Why this is worse than it looks.** `product_model` is the string that upstream publishes as
`models:` and it is on its way to deciding whether a recipe may be applied to a device. A record
claiming `product_model: not_applicable` on a phone is claiming the phone has no model. Anything
downstream that reads `not_applicable` as "this axis does not apply, skip the check" has a path
straight through a safety check.

**Fix:**

1. In the `else` branch, every Android field takes the phone test that `partition_scheme` and
   `bootloader_state` already take: `unknown` for a phone, `not_applicable` otherwise. Write it
   once as a helper rather than nineteen times as a ternary, so the next field added cannot be
   forgotten.
2. `NA()` must not decide between `unknown` and `not_applicable` from an empty string, because an
   empty string does not say which one is meant. Give it the phone context, or return `unknown`
   for a phone and let non-phone records take `not_applicable` explicitly.
3. Do not touch the `else if(a)` branch's behaviour for values `derive.sh` already returns as
   `unknown`. Those are correct.

**Prove it:** capture one phone through the browser only, skip step 2, export, and confirm every
Android field reads `unknown` rather than `not_applicable`. Then run the `slot_suffix`
reproduction above through the derived path and confirm the record says `unknown`. Then write a
test that fails if any Android field in a phone record is `not_applicable`, and prove it fails by
reverting one field.

---

## What "done" means for this batch

- `bash tests/all.sh` runs and nothing that passed before fails now.
- The two proofs above were actually carried out, not reasoned about.
- No file outside `bench-kit/START-HERE.html`, `data/schema.md` and the contributions
  validator plus its tests has changed.
- The three proofs were carried out. `not_applicable` no longer appears on any Android field of a
  phone record, by any of the three branches.
- No absolute path, no home directory and no personal address appears in any file you
  touched. `bash tests/check-public-safe.sh` still passes.

Do not report build status in a summary. Ranaji runs the suite himself.
